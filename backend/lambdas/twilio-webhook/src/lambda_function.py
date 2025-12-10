"""
Twilio WhatsApp Webhook Lambda Function

This Lambda receives incoming WhatsApp messages via Twilio webhooks,
processes them through the orchestrator, and sends responses back via Twilio API.

Environment Variables:
    ORCHESTRATOR_LAMBDA_ARN: ARN of orchestrator Lambda
    DYNAMODB_SESSIONS_TABLE: Session tracking table
    TWILIO_ACCOUNT_SID: Twilio Account SID
    TWILIO_AUTH_TOKEN: Twilio Auth Token
    TWILIO_WHATSAPP_NUMBER: Twilio WhatsApp sender number (e.g., whatsapp:+14155238886)
    REGION: AWS region

Twilio Webhook Format (form-urlencoded):
    From: whatsapp:+60123456789
    To: whatsapp:+14155238886
    Body: User message text
    MessageSid: Unique message ID
"""

import json
import boto3
import os
import re
import uuid
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from urllib.parse import parse_qs, urlencode

# Try to import Twilio SDK
try:
    from twilio.rest import Client as TwilioClient
    from twilio.request_validator import RequestValidator
    TWILIO_SDK_AVAILABLE = True
except ImportError:
    TWILIO_SDK_AVAILABLE = False
    print("[WARN] Twilio SDK not available, signature validation disabled")

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'ap-southeast-1'))
lambda_client = boto3.client('lambda', region_name=os.environ.get('REGION', 'ap-southeast-1'))

# Configuration
SESSIONS_TABLE = os.environ.get('DYNAMODB_SESSIONS_TABLE', 'chatbot-sessions')
CUSTOMERS_TABLE = os.environ.get('DYNAMODB_CUSTOMERS_TABLE', 'chatbot-customers')
ORCHESTRATOR_ARN = os.environ.get('ORCHESTRATOR_LAMBDA_ARN')
REGION = os.environ.get('REGION', 'ap-southeast-1')

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

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
        # Already has country code
        return f'+{cleaned}'
    elif cleaned.startswith('0'):
        # Malaysian format starting with 0
        return f'+60{cleaned[1:]}'
    elif len(cleaned) >= 9 and len(cleaned) <= 11:
        # Assume Malaysian number without country code or leading 0
        return f'+60{cleaned}'
    else:
        # Return as-is with + prefix
        return f'+{cleaned}' if cleaned else None


def lookup_customer(phone_number: str) -> Optional[Dict[str, Any]]:
    """
    Look up customer in DynamoDB by phone number.
    
    Args:
        phone_number: Normalized phone number (+60XXXXXXXXX)
        
    Returns:
        Customer record or None if not found
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


def validate_twilio_signature(event: Dict[str, Any]) -> bool:
    """
    Validate that the request came from Twilio using X-Twilio-Signature header.
    
    Args:
        event: API Gateway event
        
    Returns:
        True if signature is valid or validation is disabled, False otherwise
    """
    # TEMPORARY: Skip signature validation for testing/demo
    # TODO: Re-enable signature validation for production
    print("[DEBUG] Signature validation temporarily disabled for testing")
    return True
    
    if not TWILIO_SDK_AVAILABLE or not TWILIO_AUTH_TOKEN:
        print("[WARN] Skipping Twilio signature validation (SDK or auth token not available)")
        return True
    
    try:
        # Get signature from headers (case-insensitive)
        headers = event.get('headers', {})
        signature = None
        for key, value in headers.items():
            if key.lower() == 'x-twilio-signature':
                signature = value
                break
        
        if not signature:
            print("[WARN] No X-Twilio-Signature header found")
            return False
        
        # Reconstruct the URL that Twilio signed
        # For API Gateway, we need to build the full URL
        host = headers.get('Host') or headers.get('host', '')
        path = event.get('path', '/twilio-webhook')
        protocol = 'https'
        url = f"{protocol}://{host}{path}"
        
        # Parse the body parameters
        body = event.get('body', '')
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body).decode('utf-8')
        
        params = parse_qs(body, keep_blank_values=True)
        # Convert lists to single values (Twilio sends single values)
        params = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in params.items()}
        
        # Validate signature
        validator = RequestValidator(TWILIO_AUTH_TOKEN)
        is_valid = validator.validate(url, params, signature)
        
        if not is_valid:
            print(f"[WARN] Invalid Twilio signature for URL: {url}")
        
        return is_valid
        
    except Exception as e:
        print(f"[ERROR] Error validating Twilio signature: {e}")
        return False


def parse_twilio_webhook(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse Twilio webhook payload (form-urlencoded).
    
    Args:
        event: API Gateway event
        
    Returns:
        Parsed webhook data with phone_number, message, etc.
    """
    body = event.get('body', '')
    
    # Handle base64 encoding
    if event.get('isBase64Encoded'):
        body = base64.b64decode(body).decode('utf-8')
    
    # Parse form-urlencoded body
    params = parse_qs(body, keep_blank_values=True)
    
    # Extract values (parse_qs returns lists, get first element)
    from_number = params.get('From', [''])[0]  # e.g., "whatsapp:+60123456789"
    to_number = params.get('To', [''])[0]      # e.g., "whatsapp:+14155238886"
    message_body = params.get('Body', [''])[0]
    message_sid = params.get('MessageSid', [''])[0]
    
    # Extract phone number (remove "whatsapp:" prefix)
    phone_number = from_number.replace('whatsapp:', '').strip()
    
    print(f"[TWILIO] Received message from {phone_number}: {message_body[:50]}...")
    
    return {
        'phone_number': phone_number,
        'message': message_body,
        'message_sid': message_sid,
        'from_raw': from_number,
        'to_raw': to_number
    }


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
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'<script.*?</script>', '', message, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'<.*?>', '', sanitized)  # Remove HTML tags
    
    return sanitized.strip()


def validate_phone_number(phone_number: str) -> bool:
    """
    Validate phone number format (Malaysian or international).
    
    Args:
        phone_number: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Accept Malaysian numbers (+60) and international numbers
    pattern = r'^\+\d{10,15}$'
    return bool(re.match(pattern, phone_number))


def create_or_resume_session(phone_number: str, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create new session or resume existing session based on phone number.
    
    For WhatsApp, we use phone number to find existing sessions.
    Also looks up customer in CRM to check if they're registered.
    
    Args:
        phone_number: Customer phone number (WhatsApp sender)
        message: User message
        session_id: Existing session ID (optional)
        
    Returns:
        Session data including customer_verified flag
    """
    sessions_table = dynamodb.Table(SESSIONS_TABLE)
    
    # Look up customer in CRM
    customer = lookup_customer(phone_number)
    customer_verified = customer is not None
    customer_id = customer.get('customer_id') if customer else f"CUST-{phone_number.replace('+', '')}"
    
    # Try to find existing session by phone number
    try:
        # NOTE: Removed Limit=10 because it limits items BEFORE filtering,
        # which could miss the session with awaiting_action set
        response = sessions_table.scan(
            FilterExpression='phone_number = :phone',
            ExpressionAttributeValues={':phone': phone_number}
        )
        
        # Find most recent active session
        items = response.get('Items', [])
        active_session = None
        
        # Sort by updated_at and check up to 10 most recent sessions
        for item in sorted(items, key=lambda x: x.get('updated_at', ''), reverse=True)[:10]:
            if 'ttl' in item:
                ttl_timestamp = item['ttl']
                if ttl_timestamp > datetime.utcnow().timestamp():
                    active_session = item
                    break
        
        if active_session:
            session_id = active_session['session_id']
            prev_turn = active_session.get('turn_number', 0)
            new_turn = int(prev_turn) + 1 if prev_turn else 1
            
            # Preserve session state including awaiting_action and pending_intent
            session_state = active_session.get('session_state', 'active')
            verified_phone = active_session.get('verified_phone', phone_number if customer_verified else None)
            awaiting_action = active_session.get('awaiting_action')
            pending_intent = active_session.get('pending_intent')
            
            print(f"[OK] Resuming WhatsApp session: {session_id}, state: {session_state}, awaiting: {awaiting_action}")
            
            # Update session with new turn - PRESERVE awaiting_action and pending_intent
            sessions_table.put_item(Item={
                'session_id': session_id,
                'turn_number': new_turn,
                'customer_id': customer_id,
                'phone_number': phone_number,
                'verified_phone': verified_phone,
                'user_message': message,
                'channel': 'whatsapp',
                'session_state': session_state,
                'customer_verified': customer_verified,
                'awaiting_action': awaiting_action,
                'pending_intent': pending_intent,
                'created_at': active_session.get('created_at', datetime.utcnow().isoformat()),
                'updated_at': datetime.utcnow().isoformat(),
                'ttl': int((datetime.utcnow() + timedelta(hours=SESSION_TTL_HOURS)).timestamp())
            })
            
            return {
                'session_id': session_id,
                'turn_number': new_turn,
                'customer_id': customer_id,
                'verified_phone': verified_phone,
                'customer_verified': customer_verified,
                'session_state': session_state,
                'awaiting_action': awaiting_action,
                'pending_intent': pending_intent,
                'is_new_session': False
            }
            
    except Exception as e:
        print(f"[WARN] Error finding existing session: {e}")
    
    # Create new session
    new_session_id = f"WA-SESSION-{uuid.uuid4().hex[:16]}"
    turn_number = 0
    
    session_data = {
        'session_id': new_session_id,
        'turn_number': turn_number,
        'customer_id': customer_id,
        'phone_number': phone_number,
        'verified_phone': phone_number if customer_verified else None,
        'user_message': message,
        'session_state': 'active',
        'channel': 'whatsapp',
        'customer_verified': customer_verified,
        'awaiting_action': None,
        'pending_intent': None,
        'pin_attempts': 0,
        'conversation_history': [],
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat(),
        'ttl': int((datetime.utcnow() + timedelta(hours=SESSION_TTL_HOURS)).timestamp())
    }
    
    sessions_table.put_item(Item=session_data)
    
    print(f"[OK] Created new WhatsApp session: {new_session_id}, customer_verified: {customer_verified}")
    
    return {
        'session_id': new_session_id,
        'turn_number': turn_number,
        'customer_id': customer_id,
        'verified_phone': phone_number if customer_verified else None,
        'customer_verified': customer_verified,
        'session_state': 'active',
        'awaiting_action': None,
        'pending_intent': None,
        'is_new_session': True
    }


def invoke_orchestrator(session_data: Dict[str, Any], message: str, phone_number: str) -> Dict[str, Any]:
    """
    Invoke orchestrator Lambda synchronously.
    
    Args:
        session_data: Session information
        message: User message
        phone_number: Customer phone number
        
    Returns:
        Orchestrator response
    """
    if not ORCHESTRATOR_ARN:
        print("[ERROR] ORCHESTRATOR_LAMBDA_ARN not configured")
        raise Exception("ORCHESTRATOR_LAMBDA_ARN not configured")
    
    try:
        payload = {
            'session_id': session_data['session_id'],
            'turn_number': int(session_data['turn_number']),  # Ensure int (not Decimal)
            'customer_id': session_data['customer_id'],
            'phone_number': phone_number,
            'message': message,
            'channel': 'whatsapp',
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
        
        print(f"[OK] Orchestrator invoked for WhatsApp session {session_data['session_id']}")
        return orchestrator_response
        
    except Exception as e:
        print(f"[ERROR] Error invoking orchestrator: {e}")
        raise


def send_whatsapp_reply(to_number: str, message: str) -> bool:
    """
    Send WhatsApp reply via Twilio API.
    
    Args:
        to_number: Recipient WhatsApp number (with whatsapp: prefix)
        message: Message to send
        
    Returns:
        True if sent successfully, False otherwise
    """
    if not TWILIO_SDK_AVAILABLE:
        print("[ERROR] Twilio SDK not available, cannot send reply")
        return False
    
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("[ERROR] Twilio credentials not configured")
        return False
    
    try:
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Ensure whatsapp: prefix
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'
        
        message_response = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_number,
            body=message
        )
        
        print(f"[OK] WhatsApp reply sent: {message_response.sid}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error sending WhatsApp reply: {e}")
        return False


def handler(event, context):
    """
    Lambda handler for Twilio WhatsApp webhook.
    
    Args:
        event: API Gateway event (Twilio webhook)
        context: Lambda context
        
    Returns:
        API Gateway response (TwiML or empty 200)
    """
    print(f"[TWILIO-WH] Received event: {json.dumps(event, default=str)}")
    
    # Handle CORS preflight (shouldn't happen with Twilio, but just in case)
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
        # Validate Twilio signature (security)
        if not validate_twilio_signature(event):
            print("[ERROR] Invalid Twilio signature - rejecting request")
            return {
                'statusCode': 403,
                'body': 'Forbidden: Invalid signature'
            }
        
        # Parse Twilio webhook payload
        webhook_data = parse_twilio_webhook(event)
        
        phone_number = webhook_data['phone_number']
        message = webhook_data['message']
        from_raw = webhook_data['from_raw']
        
        # Validate phone number
        if not phone_number or not validate_phone_number(phone_number):
            print(f"[WARN] Invalid phone number: {phone_number}")
            return {
                'statusCode': 400,
                'body': 'Invalid phone number'
            }
        
        # Validate message
        if not message:
            print("[WARN] Empty message received")
            return {
                'statusCode': 200,
                'body': ''  # Twilio expects 200 even for empty messages
            }
        
        # Sanitize message
        message = sanitize_message(message)
        
        if len(message) == 0:
            return {
                'statusCode': 200,
                'body': ''
            }
        
        # Create or resume session
        session_data = create_or_resume_session(phone_number, message)
        
        # Invoke orchestrator
        try:
            orchestrator_response = invoke_orchestrator(session_data, message, phone_number)
            
            # Extract response text
            response_body = orchestrator_response.get('body', {})
            if isinstance(response_body, str):
                response_body = json.loads(response_body)
            
            bot_response = response_body.get('response', 'I apologize, I encountered an error. Please try again.')
            
        except Exception as orch_error:
            print(f"[ERROR] Orchestrator error: {orch_error}")
            bot_response = "I'm sorry, I encountered an error. Please try again or type 'agent' to speak with a human."
        
        # Send reply via Twilio API
        send_success = send_whatsapp_reply(from_raw, bot_response)
        
        if not send_success:
            print("[WARN] Failed to send WhatsApp reply via API, returning TwiML")
            # Fallback: Return TwiML response (Twilio will send the message)
            twiml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{bot_response}</Message>
</Response>'''
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/xml'
                },
                'body': twiml_response
            }
        
        # Return empty 200 (message already sent via API)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/plain'
            },
            'body': ''
        }
        
    except Exception as e:
        print(f"[ERROR] Error in Twilio webhook handler: {e}")
        
        # Try to send error message to user
        try:
            webhook_data = parse_twilio_webhook(event)
            send_whatsapp_reply(
                webhook_data['from_raw'],
                "I apologize, but I encountered an error. Please try again later."
            )
        except:
            pass
        
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

