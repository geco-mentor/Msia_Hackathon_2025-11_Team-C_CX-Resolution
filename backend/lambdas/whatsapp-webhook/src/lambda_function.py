"""
API Handler Lambda Function - Entry Point (API Gateway Integration)

This Lambda is the entry point for chatbot requests from Flutter app via API Gateway.
It handles:
1. Input validation (phone number, message)
2. Session creation/resumption
3. CORS preflight handling (OPTIONS method)
4. Synchronous invocation of orchestrator Lambda
5. Returns chatbot response directly to client

Environment Variables:
    ORCHESTRATOR_LAMBDA_ARN: ARN of orchestrator Lambda
    DYNAMODB_SESSIONS_TABLE: Session tracking table
    REGION: AWS region

Input Event (from API Gateway):
    {
        "httpMethod": "POST",
        "body": {
            "phone_number": "+60123456789",
            "message": "nk off vm skrg",
            "session_id": "SESSION-CUST001-123"  # Optional, for resuming
        }
    }

Output:
    {
        "session_id": "SESSION-CUST001-1234567890",
        "message": "I can help you deactivate voicemail...",
        "metadata": {
            "intent": "deactivate_voicemail",
            "grounded": false,
            "language": "EN",
            "confidence": 0.95
        },
        "requires_followup": true,
        "timestamp": "2025-12-08T10:30:00Z"
    }
"""

import json
import boto3
import os
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Make X-Ray optional (not available in all Lambda environments)
try:
    from aws_xray_sdk.core import xray_recorder
except ImportError:
    class DummyRecorder:
        def capture(self, name):
            def decorator(func):
                return func
            return decorator
    xray_recorder = DummyRecorder()

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'ap-southeast-1'))
lambda_client = boto3.client('lambda', region_name=os.environ.get('REGION', 'ap-southeast-1'))

# Configuration
SESSIONS_TABLE = os.environ.get('DYNAMODB_SESSIONS_TABLE', 'chatbot-sessions')
CUSTOMERS_TABLE = os.environ.get('DYNAMODB_CUSTOMERS_TABLE', 'chatbot-customers')
ORCHESTRATOR_ARN = os.environ.get('ORCHESTRATOR_LAMBDA_ARN')
REGION = os.environ.get('REGION', 'ap-southeast-1')

# Session TTL: 24 hours
SESSION_TTL_HOURS = 24


def normalize_phone_number(phone: str) -> Optional[str]:
    """
    Normalize Malaysian phone number to standard +60 format.
    
    Handles formats:
    - +60177967594
    - 60177967594
    - 0177967594
    - 177967594
    - +60 17 796 7594 (with spaces)
    
    Returns:
        Normalized phone number in +60XXXXXXXXX format or None
    """
    if not phone:
        return None
    
    # Remove all non-digit characters except leading +
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # Remove leading + for processing
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    # Handle different formats
    if cleaned.startswith('60'):
        return f'+{cleaned}'
    elif cleaned.startswith('0'):
        return f'+60{cleaned[1:]}'
    elif len(cleaned) >= 9 and len(cleaned) <= 11:
        return f'+60{cleaned}'
    else:
        return f'+{cleaned}' if cleaned else None


def lookup_customer(phone_number: str) -> Optional[Dict[str, Any]]:
    """
    Look up customer in DynamoDB by phone number.
    """
    if not phone_number:
        return None
    
    try:
        customers_table = dynamodb.Table(CUSTOMERS_TABLE)
        response = customers_table.get_item(
            Key={'phone_number': phone_number}
        )
        
        customer = response.get('Item')
        if customer:
            print(f"[OK] Found customer: {customer.get('customer_id')} for phone {phone_number}")
            return customer
        else:
            print(f"[INFO] Customer not found for phone: {phone_number}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error looking up customer: {e}")
        return None


@xray_recorder.capture("validate_phone_number")
def validate_phone_number(phone_number: str) -> bool:
    """
    Validate Malaysian phone number format.

    Valid formats:
        +60123456789 (10 digits)
        +60198765432 (10 digits)
        +601234567890 (11 digits - some Malaysian numbers)

    Args:
        phone_number: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    # Malaysian phone number regex: +60 followed by 9-11 digits
    pattern = r'^\+60\d{9,11}$'
    return bool(re.match(pattern, phone_number))


@xray_recorder.capture("sanitize_message")
def sanitize_message(message: str) -> str:
    """
    Sanitize user message (prevent injection attacks).

    Args:
        message: User message

    Returns:
        Sanitized message
    """
    # Limit length
    message = message[:500]

    # Remove potentially dangerous characters (basic sanitization)
    # Allow: letters, numbers, common punctuation, spaces
    # Remove: script tags, SQL injection patterns
    sanitized = re.sub(r'<script.*?</script>', '', message, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'<.*?>', '', sanitized)  # Remove HTML tags

    return sanitized.strip()


@xray_recorder.capture("create_or_resume_session")
def create_or_resume_session(phone_number: str, message: str, session_id: Optional[str] = None, channel: str = 'web') -> Dict[str, Any]:
    """
    Create new session or resume existing session.
    Also looks up customer in CRM to check if they're registered.

    Args:
        phone_number: Customer phone number
        message: User message
        session_id: Existing session ID (optional)
        channel: Channel type (web, mobile, whatsapp)

    Returns:
        Session data including customer_verified flag
    """
    sessions_table = dynamodb.Table(SESSIONS_TABLE)
    
    # Normalize phone number
    normalized_phone = normalize_phone_number(phone_number)
    if normalized_phone:
        phone_number = normalized_phone
    
    # Look up customer in CRM
    customer = lookup_customer(phone_number)
    customer_verified = customer is not None
    customer_id = customer.get('customer_id') if customer else f"CUST-{phone_number.replace('+', '')}"

    # If session_id provided, try to resume
    if session_id:
        try:
            response = sessions_table.query(
                KeyConditionExpression='session_id = :sid',
                ExpressionAttributeValues={':sid': session_id},
                ScanIndexForward=False,
                Limit=1
            )

            if 'Items' in response and len(response['Items']) > 0:
                session = response['Items'][0]
                if 'ttl' in session:
                    ttl_timestamp = session['ttl']
                    if ttl_timestamp > datetime.utcnow().timestamp():
                        print(f"[OK] Resuming session: {session_id}")

                        new_turn = int(session.get('turn_number', 0)) + 1
                        
                        # CRITICAL: Preserve session state for multi-turn flows (PIN verification)
                        awaiting_action = session.get('awaiting_action')
                        pending_intent = session.get('pending_intent')
                        session_state = session.get('session_state', 'active')
                        
                        print(f"[DEBUG] Preserving session state: awaiting={awaiting_action}, intent={pending_intent}")

                        sessions_table.put_item(Item={
                            'session_id': session_id,
                            'turn_number': new_turn,
                            'customer_id': customer_id,
                            'phone_number': phone_number,
                            'user_message': message,
                            'channel': channel,
                            'customer_verified': customer_verified,
                            'session_state': session_state,
                            'awaiting_action': awaiting_action,  # Preserve for PIN flow
                            'pending_intent': pending_intent,    # Preserve intent being verified
                            'created_at': session.get('created_at', datetime.utcnow().isoformat()),
                            'updated_at': datetime.utcnow().isoformat(),
                            'ttl': int((datetime.utcnow() + timedelta(hours=SESSION_TTL_HOURS)).timestamp())
                        })

                        return {
                            'session_id': session_id,
                            'turn_number': new_turn,
                            'customer_id': customer_id,
                            'customer_verified': customer_verified,
                            'is_new_session': False
                        }
                    else:
                        print(f"[WARN] Session expired: {session_id}")

        except Exception as e:
            print(f"[WARN] Error resuming session: {e}")

    # Create new session
    new_session_id = f"SESSION-{uuid.uuid4().hex[:16]}"
    turn_number = 0

    session_data = {
        'session_id': new_session_id,
        'turn_number': turn_number,
        'customer_id': customer_id,
        'phone_number': phone_number,
        'user_message': message,
        'session_state': 'active',
        'channel': channel,
        'customer_verified': customer_verified,
        'pin_attempts': 0,
        'conversation_history': [],
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat(),
        'ttl': int((datetime.utcnow() + timedelta(hours=SESSION_TTL_HOURS)).timestamp())
    }

    sessions_table.put_item(Item=session_data)

    print(f"[OK] Created new session: {new_session_id}, customer_verified: {customer_verified}")

    return {
        'session_id': new_session_id,
        'turn_number': turn_number,
        'customer_id': customer_id,
        'customer_verified': customer_verified,
        'is_new_session': True
    }


@xray_recorder.capture("invoke_orchestrator")
def invoke_orchestrator(session_data: Dict[str, Any], message: str, phone_number: str, channel: str = 'web') -> Dict[str, Any]:
    """
    Invoke orchestrator Lambda synchronously (for API Gateway).

    Args:
        session_data: Session information
        message: User message
        phone_number: Customer phone number
        channel: Channel type (web, mobile)

    Returns:
        Orchestrator response or error dict
    """
    if not ORCHESTRATOR_ARN:
        print("[ERROR] ORCHESTRATOR_LAMBDA_ARN not configured")
        raise Exception("ORCHESTRATOR_LAMBDA_ARN not configured")

    try:
        payload = {
            'session_id': session_data['session_id'],
            'turn_number': int(session_data['turn_number']),
            'customer_id': session_data['customer_id'],
            'phone_number': phone_number,
            'message': message,
            'channel': channel,  # web or mobile
            'is_new_session': session_data.get('is_new_session', False)
        }

        response = lambda_client.invoke(
            FunctionName=ORCHESTRATOR_ARN,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        orchestrator_response = json.loads(response['Payload'].read())

        if response.get('FunctionError'):
            raise Exception(f"Orchestrator error: {orchestrator_response}")

        print(f"[OK] Orchestrator invoked sync for session {session_data['session_id']}")
        return orchestrator_response

    except Exception as e:
        print(f"[ERROR] Error invoking orchestrator: {e}")
        raise


@xray_recorder.capture("handler")
def handler(event, context):
    """
    Lambda handler for API entry point.

    Args:
        event: API Gateway event
        context: Lambda context

    Returns:
        API Gateway response
    """
    print(f"[API] API Handler invoked with event: {json.dumps(event, default=str)}")

    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': ''
        }

    try:
        # Parse input from API Gateway
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            # Direct invocation (testing)
            body = event

        # Extract and validate parameters
        phone_number = body.get('phone_number', '').strip()
        message = body.get('message', '').strip()
        session_id = body.get('session_id')
        
        # Detect channel: mobile app passes 'channel' field, otherwise assume web
        channel = body.get('channel', 'web')
        
        # Normalize phone number to +60 format
        normalized_phone = normalize_phone_number(phone_number)
        if normalized_phone:
            phone_number = normalized_phone

        # Validation
        if not phone_number:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # CORS
                },
                'body': json.dumps({
                    'error': 'Missing required field: phone_number'
                })
            }

        if not validate_phone_number(phone_number):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid phone number format. Expected: +60XXXXXXXXX'
                })
            }

        if not message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing required field: message'
                })
            }

        # Sanitize message
        message = sanitize_message(message)

        if len(message) == 0:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Message is empty after sanitization'
                })
            }

        # Create or resume session
        session_data = create_or_resume_session(phone_number, message, session_id, channel)

        # Invoke orchestrator synchronously and get response
        try:
            orchestrator_response = invoke_orchestrator(session_data, message, phone_number, channel)

            # Extract response data from orchestrator
            response_body = orchestrator_response.get('body', {})
            if isinstance(response_body, str):
                response_body = json.loads(response_body)

            # Return orchestrator response to client
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'session_id': session_data['session_id'],
                    'message': response_body.get('response', 'Processing...'),
                    'metadata': {
                        'intent': response_body.get('intent'),
                        'grounded': response_body.get('grounded', False),
                        'language': response_body.get('language', 'EN'),
                        'confidence': response_body.get('confidence')
                    },
                    'requires_followup': response_body.get('requires_followup', False),
                    'escalate': response_body.get('escalate', False),
                    'timestamp': response_body.get('timestamp', datetime.utcnow().isoformat() + 'Z')
                })
            }

        except Exception as orch_error:
            print(f"[ERROR] Orchestrator error: {orch_error}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Failed to process message',
                    'session_id': session_data['session_id'],
                    'message': 'Sorry, I encountered an error. Please try again.'
                })
            }

    except Exception as e:
        print(f"[ERROR] Error in API Handler: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
