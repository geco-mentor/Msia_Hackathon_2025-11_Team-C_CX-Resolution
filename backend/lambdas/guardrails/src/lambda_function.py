"""
Guardrails Lambda Function - Business Logic Security

REFACTORED to use AWS Best Practices:
- Bedrock Guardrails handles: abuse detection, PII, content filtering
- This Lambda handles: PIN verification, rate limiting (business-specific logic)
- Simplified architecture - no redundant code

Environment Variables:
    DYNAMODB_CUSTOMERS_TABLE: Customer data table
    DYNAMODB_SESSIONS_TABLE: Session tracking table
    MAX_PIN_ATTEMPTS: Maximum failed PIN attempts (default: 3)
    PIN_LOCKOUT_MINUTES: Account lockout duration (default: 15)
    REGION: AWS region

Input Event:
    {
        "action": "verify_pin",
        "session_id": "SESSION-CUST001-123",
        "phone_number": "+60123456789",
        "security_pin": "1234"
    }

Output:
    {
        "authorized": true/false,
        "pin_verified": true/false,
        "rate_limit_exceeded": false,
        "error": "error message if any",
        "attempts_remaining": 2
    }
"""

import json
import boto3
import os
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Any
from aws_xray_sdk.core import xray_recorder

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'ap-southeast-1'))

# Configuration
CUSTOMERS_TABLE = os.environ.get('DYNAMODB_CUSTOMERS_TABLE', 'chatbot-customers')
SESSIONS_TABLE = os.environ.get('DYNAMODB_SESSIONS_TABLE', 'chatbot-sessions')
MAX_PIN_ATTEMPTS = int(os.environ.get('MAX_PIN_ATTEMPTS', '3'))
PIN_LOCKOUT_MINUTES = int(os.environ.get('PIN_LOCKOUT_MINUTES', '15'))


@xray_recorder.capture("verify_pin")
def verify_pin(phone_number: str, provided_pin: str) -> Dict[str, Any]:
    """
    Verify PIN using PBKDF2-HMAC-SHA256 with constant-time comparison.

    SECURITY:
    - Uses constant-time comparison (hmac.compare_digest) to prevent timing attacks
    - NEVER logs plaintext PINs
    - Hashes provided PIN with stored salt before comparison

    Args:
        phone_number: Customer phone number
        provided_pin: PIN provided by user (plaintext)

    Returns:
        {
            "verified": true/false,
            "locked": true/false,
            "error": "error message"
        }
    """
    try:
        # Get customer record from DynamoDB
        customers_table = dynamodb.Table(CUSTOMERS_TABLE)
        response = customers_table.get_item(
            Key={'phone_number': phone_number}
        )

        if 'Item' not in response:
            print(f"[ERROR] Customer not found: {phone_number}")
            return {
                "verified": False,
                "locked": False,
                "error": "Customer not found"
            }

        customer = response['Item']

        # Check if account is locked
        if customer.get('pin_locked_until'):
            locked_until = datetime.fromisoformat(customer['pin_locked_until'])
            if datetime.utcnow() < locked_until:
                minutes_left = int((locked_until - datetime.utcnow()).total_seconds() / 60) + 1
                print(f"[LOCKED] Account locked until {locked_until}")
                return {
                    "verified": False,
                    "locked": True,
                    "error": f"Account locked due to failed PIN attempts. Try again in {minutes_left} minutes."
                }
            else:
                # Lockout period expired, unlock account
                print(f"[UNLOCK] Lockout period expired, unlocking account")
                customers_table.update_item(
                    Key={'phone_number': phone_number},
                    UpdateExpression="REMOVE pin_locked_until"
                )

        # Get stored PIN hash and salt
        stored_hash = customer.get('security_pin_hash')
        salt_hex = customer.get('salt')

        if not stored_hash or not salt_hex:
            print(f"[ERROR] Missing PIN hash or salt for customer {phone_number}")
            return {
                "verified": False,
                "locked": False,
                "error": "Invalid customer data"
            }

        # Hash the provided PIN with the stored salt
        salt = bytes.fromhex(salt_hex)
        computed_hash = hashlib.pbkdf2_hmac(
            'sha256',
            provided_pin.encode('utf-8'),
            salt,
            100000  # 100,000 iterations
        )
        computed_hash_hex = computed_hash.hex()

        # Constant-time comparison (prevents timing attacks)
        pin_matches = hmac.compare_digest(computed_hash_hex, stored_hash)

        if pin_matches:
            print(f"[OK] PIN verified for {phone_number}")
            return {
                "verified": True,
                "locked": False,
                "error": None
            }
        else:
            print(f"[ERROR] PIN mismatch for {phone_number}")
            return {
                "verified": False,
                "locked": False,
                "error": "Incorrect PIN"
            }

    except Exception as e:
        print(f"[ERROR] Error verifying PIN: {e}")
        return {
            "verified": False,
            "locked": False,
            "error": f"PIN verification failed: {str(e)}"
        }


@xray_recorder.capture("track_failed_attempt")
def track_failed_attempt(session_id: str, phone_number: str) -> Dict[str, Any]:
    """
    Track failed PIN attempt and lock account after MAX_PIN_ATTEMPTS.

    Args:
        session_id: Session ID
        phone_number: Customer phone number

    Returns:
        {
            "locked": true/false,
            "attempts_remaining": int,
            "lock_until": ISO timestamp (if locked)
        }
    """
    try:
        sessions_table = dynamodb.Table(SESSIONS_TABLE)

        # Get current session
        response = sessions_table.query(
            KeyConditionExpression='session_id = :sid',
            ExpressionAttributeValues={':sid': session_id},
            ScanIndexForward=False,  # Latest first
            Limit=1
        )

        if 'Items' not in response or len(response['Items']) == 0:
            print(f"[WARN] Session not found: {session_id}, creating new session record")
            current_attempts = 0
        else:
            session = response['Items'][0]
            current_attempts = session.get('pin_attempts', 0)

        # Increment attempts
        new_attempts = current_attempts + 1

        # Update session with new attempt count
        if response.get('Items'):
            sessions_table.update_item(
                Key={
                    'session_id': session_id,
                    'turn_number': response['Items'][0]['turn_number']
                },
                UpdateExpression="SET pin_attempts = :attempts",
                ExpressionAttributeValues={':attempts': new_attempts}
            )

        print(f"[INFO] Failed PIN attempt #{new_attempts} for session {session_id}")

        # Check if should lock account
        if new_attempts >= MAX_PIN_ATTEMPTS:
            # Lock account for PIN_LOCKOUT_MINUTES
            lock_until = datetime.utcnow() + timedelta(minutes=PIN_LOCKOUT_MINUTES)
            lock_until_iso = lock_until.isoformat()

            # Update customer record with lockout timestamp
            customers_table = dynamodb.Table(CUSTOMERS_TABLE)
            customers_table.update_item(
                Key={'phone_number': phone_number},
                UpdateExpression="SET pin_locked_until = :lock_time",
                ExpressionAttributeValues={':lock_time': lock_until_iso}
            )

            print(f"[LOCKED] Account locked until {lock_until_iso}")

            return {
                "locked": True,
                "attempts_remaining": 0,
                "lock_until": lock_until_iso
            }

        # Not locked yet
        attempts_remaining = MAX_PIN_ATTEMPTS - new_attempts
        return {
            "locked": False,
            "attempts_remaining": attempts_remaining,
            "lock_until": None
        }

    except Exception as e:
        print(f"[ERROR] Error tracking failed attempt: {e}")
        return {
            "locked": False,
            "attempts_remaining": 0,
            "error": str(e)
        }


@xray_recorder.capture("reset_pin_attempts")
def reset_pin_attempts(session_id: str) -> bool:
    """
    Reset PIN attempt counter after successful verification.

    Args:
        session_id: Session ID

    Returns:
        Success status
    """
    try:
        sessions_table = dynamodb.Table(SESSIONS_TABLE)

        # Get current session
        response = sessions_table.query(
            KeyConditionExpression='session_id = :sid',
            ExpressionAttributeValues={':sid': session_id},
            ScanIndexForward=False,
            Limit=1
        )

        if 'Items' in response and len(response['Items']) > 0:
            sessions_table.update_item(
                Key={
                    'session_id': session_id,
                    'turn_number': response['Items'][0]['turn_number']
                },
                UpdateExpression="SET pin_attempts = :zero",
                ExpressionAttributeValues={':zero': 0}
            )
            print(f"[OK] Reset PIN attempts for session {session_id}")
            return True

        return False

    except Exception as e:
        print(f"[ERROR] Error resetting PIN attempts: {e}")
        return False


@xray_recorder.capture("check_authorization")
def check_authorization(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main authorization check - PIN verification and rate limiting.

    NOTE: Abusive language detection is handled by Bedrock Guardrails (not here).

    Args:
        event: Input event

    Returns:
        Authorization result
    """
    action = event.get('action', 'verify_pin')
    session_id = event.get('session_id')
    phone_number = event.get('phone_number')
    provided_pin = event.get('security_pin')

    result = {
        "authorized": False,
        "pin_verified": False,
        "rate_limit_exceeded": False,
        "error": None,
        "attempts_remaining": MAX_PIN_ATTEMPTS
    }

    # Verify PIN if provided
    if action == 'verify_pin' and provided_pin:
        if not phone_number:
            result["error"] = "Phone number required for PIN verification"
            return result

        pin_result = verify_pin(phone_number, provided_pin)

        if pin_result.get("locked"):
            result["rate_limit_exceeded"] = True
            result["error"] = pin_result["error"]
            result["attempts_remaining"] = 0
            return result

        if pin_result.get("verified"):
            result["pin_verified"] = True
            result["authorized"] = True
            # Reset failed attempts
            if session_id:
                reset_pin_attempts(session_id)
        else:
            # Track failed attempt
            if session_id:
                attempt_result = track_failed_attempt(session_id, phone_number)
                result["attempts_remaining"] = attempt_result.get("attempts_remaining", 0)

                if attempt_result.get("locked"):
                    result["rate_limit_exceeded"] = True
                    result["error"] = f"Account locked. Too many failed PIN attempts. Locked until {attempt_result['lock_until']}."
                else:
                    result["error"] = f"Incorrect PIN. {result['attempts_remaining']} attempts remaining."

    return result


@xray_recorder.capture("handler")
def handler(event, context):
    """
    Lambda handler for Guardrails (Business Logic only).

    NOTE: Content safety (abuse, PII) is handled by Bedrock Guardrails.
    This Lambda only handles PIN verification and rate limiting.

    Args:
        event: Input event
        context: Lambda context

    Returns:
        Authorization result
    """
    print(f"[GUARD] Guardrails invoked with event: {json.dumps(event, default=str)}")

    try:
        # Parse input
        if isinstance(event, str):
            event = json.loads(event)

        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event

        # Check authorization
        result = check_authorization(body)

        # Return result
        response = {
            'statusCode': 200 if result['authorized'] else 403,
            'body': json.dumps(result)
        }

        return response if 'body' in event else result

    except Exception as e:
        print(f"[ERROR] Error in Guardrails: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'authorized': False
            })
        }
