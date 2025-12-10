"""
CRM Mock Lambda Function - Voicemail Operations

This Lambda simulates CRM API calls for voicemail management:
1. Activate voicemail
2. Deactivate voicemail
3. Check voicemail status

CRITICAL: Implements idempotency to prevent duplicate operations.

Environment Variables:
    DYNAMODB_CUSTOMERS_TABLE: Customer data table
    IDEMPOTENCY_TABLE: Table for tracking completed operations (chatbot-sessions)
    REGION: AWS region

Input Event:
    {
        "action": "deactivate" | "activate" | "check_status",
        "phone_number": "+60123456789",
        "session_id": "SESSION-CUST001-123",  # For idempotency
        "customer_id": "CUST001"
    }

Output:
    {
        "success": true/false,
        "action": "deactivate_voicemail",
        "customer_id": "CUST001",
        "voicemail_status": "inactive" | "active",
        "timestamp": "2024-12-07T15:30:00Z",
        "idempotent": false,  # true if already processed
        "error": "error message if failed"
    }
"""

import json
import boto3
import os
from datetime import datetime
from typing import Dict, Any, Optional
from aws_xray_sdk.core import xray_recorder

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'ap-southeast-1'))

# Configuration
CUSTOMERS_TABLE = os.environ.get('DYNAMODB_CUSTOMERS_TABLE', 'chatbot-customers')
IDEMPOTENCY_TABLE = os.environ.get('IDEMPOTENCY_TABLE', 'chatbot-sessions')


@xray_recorder.capture("check_idempotency")
def check_idempotency(session_id: str, action: str) -> Optional[Dict[str, Any]]:
    """
    Check if this operation was already completed (idempotency).

    Args:
        session_id: Session ID
        action: CRM action (e.g., "deactivate_voicemail")

    Returns:
        Previous result if operation already completed, None otherwise
    """
    try:
        idempotency_key = f"{session_id}:{action}"

        # Query session table for this exact operation
        sessions_table = dynamodb.Table(IDEMPOTENCY_TABLE)
        response = sessions_table.query(
            KeyConditionExpression='session_id = :sid',
            ExpressionAttributeValues={':sid': session_id},
            ScanIndexForward=False,
            Limit=1
        )

        if 'Items' in response and len(response['Items']) > 0:
            session = response['Items'][0]
            completed_action = session.get('crm_action_completed')

            if completed_action == idempotency_key:
                print(f"[IDEMPOTENT] Request detected: {idempotency_key}")
                # Return cached result
                return session.get('crm_result', {
                    "success": True,
                    "message": "Operation already completed",
                    "idempotent": True
                })

        return None

    except Exception as e:
        print(f"[WARN] Error checking idempotency: {e}")
        # On error, proceed with operation (fail open)
        return None


@xray_recorder.capture("mark_completed")
def mark_operation_completed(session_id: str, action: str, result: Dict[str, Any]) -> bool:
    """
    Mark operation as completed for idempotency tracking.

    Args:
        session_id: Session ID
        action: CRM action
        result: Operation result to cache

    Returns:
        Success status
    """
    try:
        idempotency_key = f"{session_id}:{action}"
        sessions_table = dynamodb.Table(IDEMPOTENCY_TABLE)

        # Get current session to update
        response = sessions_table.query(
            KeyConditionExpression='session_id = :sid',
            ExpressionAttributeValues={':sid': session_id},
            ScanIndexForward=False,
            Limit=1
        )

        if 'Items' in response and len(response['Items']) > 0:
            session = response['Items'][0]

            sessions_table.update_item(
                Key={
                    'session_id': session_id,
                    'turn_number': session['turn_number']
                },
                UpdateExpression="SET crm_action_completed = :key, crm_result = :result",
                ExpressionAttributeValues={
                    ':key': idempotency_key,
                    ':result': result
                }
            )

            print(f"[OK] Marked operation as completed: {idempotency_key}")
            return True

        return False

    except Exception as e:
        print(f"[WARN] Error marking operation completed: {e}")
        return False


@xray_recorder.capture("deactivate_voicemail")
def deactivate_voicemail(phone_number: str, customer_id: str, session_id: str) -> Dict[str, Any]:
    """
    Deactivate voicemail for customer.

    Args:
        phone_number: Customer phone number
        customer_id: Customer ID
        session_id: Session ID

    Returns:
        Operation result
    """
    action = "deactivate_voicemail"

    # Check idempotency
    cached_result = check_idempotency(session_id, action)
    if cached_result:
        cached_result['idempotent'] = True
        return cached_result

    try:
        customers_table = dynamodb.Table(CUSTOMERS_TABLE)

        # Update customer record
        customers_table.update_item(
            Key={'phone_number': phone_number},
            UpdateExpression="SET voicemail_active = :inactive, updated_at = :timestamp",
            ExpressionAttributeValues={
                ':inactive': False,
                ':timestamp': datetime.utcnow().isoformat()
            }
        )

        result = {
            "success": True,
            "action": action,
            "customer_id": customer_id,
            "voicemail_status": "inactive",
            "timestamp": datetime.utcnow().isoformat(),
            "idempotent": False
        }

        # Mark as completed for idempotency
        mark_operation_completed(session_id, action, result)

        print(f"[OK] Deactivated voicemail for customer {customer_id}")

        return result

    except Exception as e:
        print(f"[ERROR] Error deactivating voicemail: {e}")
        return {
            "success": False,
            "action": action,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@xray_recorder.capture("activate_voicemail")
def activate_voicemail(phone_number: str, customer_id: str, session_id: str) -> Dict[str, Any]:
    """
    Activate voicemail for customer.

    Args:
        phone_number: Customer phone number
        customer_id: Customer ID
        session_id: Session ID

    Returns:
        Operation result
    """
    action = "activate_voicemail"

    # Check idempotency
    cached_result = check_idempotency(session_id, action)
    if cached_result:
        cached_result['idempotent'] = True
        return cached_result

    try:
        customers_table = dynamodb.Table(CUSTOMERS_TABLE)

        # Update customer record
        customers_table.update_item(
            Key={'phone_number': phone_number},
            UpdateExpression="SET voicemail_active = :active, updated_at = :timestamp",
            ExpressionAttributeValues={
                ':active': True,
                ':timestamp': datetime.utcnow().isoformat()
            }
        )

        result = {
            "success": True,
            "action": action,
            "customer_id": customer_id,
            "voicemail_status": "active",
            "timestamp": datetime.utcnow().isoformat(),
            "idempotent": False
        }

        # Mark as completed for idempotency
        mark_operation_completed(session_id, action, result)

        print(f"[OK] Activated voicemail for customer {customer_id}")

        return result

    except Exception as e:
        print(f"[ERROR] Error activating voicemail: {e}")
        return {
            "success": False,
            "action": action,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@xray_recorder.capture("check_voicemail_status")
def check_voicemail_status(phone_number: str, customer_id: str) -> Dict[str, Any]:
    """
    Check current voicemail status for customer.

    Args:
        phone_number: Customer phone number
        customer_id: Customer ID

    Returns:
        Status result
    """
    try:
        customers_table = dynamodb.Table(CUSTOMERS_TABLE)

        # Get customer record
        response = customers_table.get_item(
            Key={'phone_number': phone_number}
        )

        if 'Item' not in response:
            return {
                "success": False,
                "error": "Customer not found",
                "timestamp": datetime.utcnow().isoformat()
            }

        customer = response['Item']
        voicemail_active = customer.get('voicemail_active', False)

        print(f"[OK] Voicemail status for {customer_id}: {'active' if voicemail_active else 'inactive'}")

        return {
            "success": True,
            "action": "check_status",
            "customer_id": customer_id,
            "voicemail_status": "active" if voicemail_active else "inactive",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"[ERROR] Error checking voicemail status: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@xray_recorder.capture("handler")
def handler(event, context):
    """
    Lambda handler for CRM Mock.

    Args:
        event: Input event
        context: Lambda context

    Returns:
        CRM operation result
    """
    print(f"[CRM] CRM Mock invoked with event: {json.dumps(event, default=str)}")

    try:
        # Parse input
        if isinstance(event, str):
            event = json.loads(event)

        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event

        # Extract parameters
        action = body.get('action', 'check_status')
        phone_number = body.get('phone_number')
        customer_id = body.get('customer_id')
        session_id = body.get('session_id')

        if not phone_number or not customer_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required fields: phone_number, customer_id'
                })
            }

        # Route to appropriate CRM action
        if action == 'deactivate':
            if not session_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': 'session_id required for idempotency'
                    })
                }
            result = deactivate_voicemail(phone_number, customer_id, session_id)

        elif action == 'activate':
            if not session_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': 'session_id required for idempotency'
                    })
                }
            result = activate_voicemail(phone_number, customer_id, session_id)

        elif action == 'check_status':
            result = check_voicemail_status(phone_number, customer_id)

        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'Unknown action: {action}. Supported: deactivate, activate, check_status'
                })
            }

        # Return result
        response = {
            'statusCode': 200 if result.get('success') else 500,
            'body': json.dumps(result, default=str)
        }

        return response if 'body' in event else result

    except Exception as e:
        print(f"[ERROR] Error in CRM Mock: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'success': False
            })
        }
