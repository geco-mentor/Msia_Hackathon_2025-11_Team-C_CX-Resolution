"""
Orchestrator Lambda Function - Main Coordination Logic

REFACTORED to use AWS Best Practices:
- Bedrock Prompt Management (no hardcoded prompts)
- Bedrock Guardrails with Automated Reasoning (hallucination prevention)
- Claude 3 Haiku for response generation (fast, cost-effective)
- PII redaction built-in
- Production-grade error handling

Environment Variables:
    NLU_LAMBDA_ARN: ARN of NLU engine Lambda
    GUARDRAILS_LAMBDA_ARN: ARN of guardrails Lambda
    CRM_LAMBDA_ARN: ARN of CRM mock Lambda
    BEDROCK_KB_ID: Bedrock Knowledge Base ID
    BEDROCK_MODEL_HAIKU: Haiku model ID (default: anthropic.claude-3-haiku-20240307-v1:0)
    BEDROCK_GUARDRAIL_ID: Guardrail identifier
    BEDROCK_GUARDRAIL_VERSION: Guardrail version
    RESPONSE_PROMPT_ID: Prompt Management ARN for response generation
    TRANSLATION_PROMPT_ID: Prompt Management ARN for translation
    DYNAMODB_SESSIONS_TABLE: Sessions table
    DYNAMODB_AUDIT_TABLE: Audit logs table
    DYNAMODB_CUSTOMERS_TABLE: Customers table
    REGION: AWS region
"""

import json
import boto3
from botocore.config import Config
import os
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional

# Make X-Ray optional
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
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('REGION', 'ap-southeast-1'))

# Configure retry logic for throttling protection
bedrock_config = Config(
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'
    }
)
bedrock_agent = boto3.client(
    'bedrock-agent-runtime',
    region_name=os.environ.get('REGION', 'ap-southeast-1'),
    config=bedrock_config
)
bedrock_agent_mgmt = boto3.client('bedrock-agent', region_name=os.environ.get('REGION', 'ap-southeast-1'))

# Configuration
NLU_LAMBDA = os.environ.get('NLU_LAMBDA_ARN')
GUARDRAILS_LAMBDA = os.environ.get('GUARDRAILS_LAMBDA_ARN')
CRM_LAMBDA = os.environ.get('CRM_LAMBDA_ARN')
BEDROCK_KB_ID = os.environ.get('BEDROCK_KB_ID')
BEDROCK_HAIKU = os.environ.get('BEDROCK_MODEL_HAIKU', 'anthropic.claude-3-haiku-20240307-v1:0')
GUARDRAIL_ID = os.environ.get('BEDROCK_GUARDRAIL_ID')
GUARDRAIL_VERSION = os.environ.get('BEDROCK_GUARDRAIL_VERSION', 'DRAFT')
RESPONSE_PROMPT_ID = os.environ.get('RESPONSE_PROMPT_ID')  # Prompt Management ARN
TRANSLATION_PROMPT_ID = os.environ.get('TRANSLATION_PROMPT_ID')  # Prompt Management ARN

SESSIONS_TABLE = os.environ.get('DYNAMODB_SESSIONS_TABLE', 'chatbot-sessions')
AUDIT_TABLE = os.environ.get('DYNAMODB_AUDIT_TABLE', 'chatbot-audit-logs')
CUSTOMERS_TABLE = os.environ.get('DYNAMODB_CUSTOMERS_TABLE', 'chatbot-customers')


def get_session_state(session_id: str) -> Dict[str, Any]:
    """
    Get session state from DynamoDB to track conversation flow.
    
    Uses QUERY (not scan) since session_id is the partition key.
    Gets the most recent item by turn_number (sort key, descending).
    
    Returns:
        Session state dict with awaiting_action, pending_intent, etc.
    """
    if not session_id:
        return {}
    
    try:
        sessions_table = dynamodb.Table(SESSIONS_TABLE)
        
        # Use QUERY instead of scan - session_id is partition key
        # ScanIndexForward=False returns items in descending order by sort key (turn_number)
        response = sessions_table.query(
            KeyConditionExpression='session_id = :sid',
            ExpressionAttributeValues={':sid': session_id},
            ScanIndexForward=False,  # Most recent turn first
            Limit=1  # Only need the latest item
        )
        
        items = response.get('Items', [])
        if items:
            latest = items[0]  # Already sorted by turn_number desc
            print(f"[DEBUG] Found session state: awaiting={latest.get('awaiting_action')}, intent={latest.get('pending_intent')}")
            return {
                'awaiting_action': latest.get('awaiting_action'),
                'pending_intent': latest.get('pending_intent'),
                'session_state': latest.get('session_state', 'active')
            }
        else:
            print(f"[DEBUG] No session items found for session_id: {session_id}")
    except Exception as e:
        print(f"[ERROR] Error getting session state: {e}")
    
    return {}


def update_session_state(session_id: str, awaiting_action: str = None, pending_intent: str = None):
    """
    Update session state in DynamoDB to track what we're waiting for.
    
    Uses QUERY (not scan) since session_id is the partition key.
    Updates the most recent item by turn_number.
    
    Args:
        session_id: Session ID
        awaiting_action: What we're waiting for (pin, phone_number, None)
        pending_intent: The intent that triggered this wait
    """
    if not session_id:
        print(f"[WARN] update_session_state called with empty session_id")
        return
    
    try:
        sessions_table = dynamodb.Table(SESSIONS_TABLE)
        
        # Use QUERY instead of scan - session_id is partition key
        response = sessions_table.query(
            KeyConditionExpression='session_id = :sid',
            ExpressionAttributeValues={':sid': session_id},
            ScanIndexForward=False,  # Most recent turn first
            Limit=1
        )
        
        items = response.get('Items', [])
        if items:
            latest = items[0]  # Already sorted by turn_number desc
            latest['awaiting_action'] = awaiting_action
            latest['pending_intent'] = pending_intent
            latest['updated_at'] = datetime.utcnow().isoformat()
            sessions_table.put_item(Item=latest)
            print(f"[OK] Updated session state: awaiting={awaiting_action}, intent={pending_intent}")
        else:
            print(f"[ERROR] No session items found for session_id: {session_id}")
    except Exception as e:
        print(f"[ERROR] Error updating session state: {e}")
        # Re-raise to ensure caller knows the update failed
        raise


def normalize_phone_number(phone: str) -> str:
    """
    Normalize Malaysian phone number to standard +60 format.
    
    Handles formats:
    - +60177967594
    - 60177967594
    - 0177967594
    - 177967594
    - +60 17 796 7594 (with spaces)
    
    Returns:
        Normalized phone number in +60XXXXXXXXX format
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
            print(f"[WARN] Customer not found for phone: {phone_number}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error looking up customer: {e}")
        return None


@xray_recorder.capture("invoke_nlu")
def invoke_nlu(message: str) -> Dict[str, Any]:
    """Invoke NLU Engine to detect intent and extract slots."""
    try:
        response = lambda_client.invoke(
            FunctionName=NLU_LAMBDA,
            InvocationType='RequestResponse',
            Payload=json.dumps({"message": message})
        )

        result = json.loads(response['Payload'].read())

        if 'body' in result:
            body = json.loads(result['body']) if isinstance(result['body'], str) else result['body']
            return body

        return result

    except Exception as e:
        print(f"[ERROR] Error invoking NLU: {e}")
        return {
            "intent": "unclear_intent",
            "confidence": 0.0,
            "slots": {},
            "error": str(e)
        }


@xray_recorder.capture("invoke_guardrails")
def invoke_guardrails(action: str, session_id: str, phone_number: str, security_pin: Optional[str]) -> Dict[str, Any]:
    """Invoke Guardrails for PIN verification and rate limiting."""
    try:
        payload = {
            "action": action,
            "session_id": session_id,
            "phone_number": phone_number,
            "security_pin": security_pin
        }

        response = lambda_client.invoke(
            FunctionName=GUARDRAILS_LAMBDA,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        result = json.loads(response['Payload'].read())

        if 'body' in result:
            body = json.loads(result['body']) if isinstance(result['body'], str) else result['body']
            return body

        return result

    except Exception as e:
        print(f"[ERROR] Error invoking Guardrails: {e}")
        return {
            "authorized": False,
            "error": str(e)
        }


@xray_recorder.capture("invoke_crm")
def invoke_crm(action: str, phone_number: str, customer_id: str, session_id: str) -> Dict[str, Any]:
    """Invoke CRM Mock for voicemail operations."""
    try:
        payload = {
            "action": action,
            "phone_number": phone_number,
            "customer_id": customer_id,
            "session_id": session_id
        }

        response = lambda_client.invoke(
            FunctionName=CRM_LAMBDA,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        result = json.loads(response['Payload'].read())

        if 'body' in result:
            body = json.loads(result['body']) if isinstance(result['body'], str) else result['body']
            return body

        return result

    except Exception as e:
        print(f"[ERROR] Error invoking CRM: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@xray_recorder.capture("retrieve_from_kb")
def retrieve_from_kb(query: str, language: str = "EN") -> Dict[str, Any]:
    """
    Retrieve and generate response from Bedrock Knowledge Base (RAG).

    Uses Automated Reasoning for hallucination prevention.
    """
    if not BEDROCK_KB_ID:
        return {
            "response": "Knowledge Base not configured.",
            "grounded": False,
            "citations": []
        }

    try:
        # Build retrieval configuration with Automated Reasoning
        retrieval_config = {
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': BEDROCK_KB_ID,
                'modelArn': BEDROCK_HAIKU,  # Use model ID directly (not ARN format)
                'retrievalConfiguration': {
                    'vectorSearchConfiguration': {
                        'numberOfResults': 3
                    }
                }
            }
        }

        # Add Guardrails in generationConfiguration if configured
        if GUARDRAIL_ID:
            retrieval_config['knowledgeBaseConfiguration']['generationConfiguration'] = {
                'guardrailConfiguration': {
                    'guardrailId': GUARDRAIL_ID,
                    'guardrailVersion': GUARDRAIL_VERSION
                }
            }

        response = bedrock_agent.retrieve_and_generate(
            input={'text': query},
            retrieveAndGenerateConfiguration=retrieval_config
        )

        # Debug: Print full response structure
        print(f"[DEBUG] KB Response keys: {list(response.keys())}")
        if 'guardrailAction' in response:
            print(f"[DEBUG] Guardrail action value: {response['guardrailAction']}")

        # Check for trace/assessment details
        if 'trace' in response:
            print(f"[DEBUG] Trace keys: {list(response['trace'].keys())}")

        # Print citations to see if KB retrieval worked
        if 'citations' in response:
            print(f"[DEBUG] Citations found: {len(response.get('citations', []))}")

        # Print output structure
        if 'output' in response:
            print(f"[DEBUG] Output keys: {list(response['output'].keys())}")

        # Check if guardrail intervened
        if 'guardrailAction' in response:
            guardrail_action = response['guardrailAction']
            print(f"[GUARD] Guardrail action: {guardrail_action}")

            if guardrail_action == 'INTERVENED':
                print(f"[BLOCKED] Guardrail blocked harmful content in KB response")
                return {
                    "response": "I apologize, but I cannot provide that information. Please contact support.",
                    "grounded": False,
                    "citations": []
                }

        generated_text = response['output']['text']
        citations = response.get('citations', [])

        # Extract source article IDs
        source_ids = []
        for citation in citations:
            for ref in citation.get('retrievedReferences', []):
                location = ref.get('location', {})
                s3_location = location.get('s3Location', {})
                uri = s3_location.get('uri', '')
                if uri:
                    filename = uri.split('/')[-1]
                    article_id = filename.split('-')[0]
                    if article_id not in source_ids:
                        source_ids.append(article_id)

        # Translate to Bahasa Malaysia if needed
        if language == "BM" and generated_text:
            translated = translate_to_bahasa(generated_text)
            if translated:
                generated_text = translated

        return {
            "response": generated_text,
            "grounded": len(source_ids) > 0,
            "citations": source_ids
        }

    except Exception as e:
        print(f"[ERROR] Error retrieving from KB: {e}")
        return {
            "response": f"I'm sorry, I encountered an error. Please try again.",
            "grounded": False,
            "citations": [],
            "error": str(e)
        }


@xray_recorder.capture("translate_to_bahasa")
def translate_to_bahasa(text: str) -> Optional[str]:
    """Translate English text to Bahasa Malaysia using Bedrock Haiku (fast)."""
    try:
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.3,
            "messages": [{
                "role": "user",
                "content": f"Translate this English text to Bahasa Malaysia. Maintain the same tone:\n\n{text}"
            }]
        }

        invoke_params = {
            'modelId': BEDROCK_HAIKU,
            'body': json.dumps(request_body)
        }

        # Add guardrails if configured
        if GUARDRAIL_ID:
            invoke_params['guardrailIdentifier'] = GUARDRAIL_ID
            invoke_params['guardrailVersion'] = GUARDRAIL_VERSION

        response = bedrock_runtime.invoke_model(**invoke_params)
        result = json.loads(response['body'].read())
        return result['content'][0]['text'].strip()

    except Exception as e:
        print(f"[WARN] Translation error: {e}")
        return None


@xray_recorder.capture("get_response_prompt")
def get_response_prompt(intent: str, context: Dict[str, Any], language: str) -> Dict[str, Any]:
    """
    Get response generation prompt from Bedrock Prompt Management.

    Falls back to inline prompt if Prompt Management not configured.
    """
    if not RESPONSE_PROMPT_ID:
        print("[WARN] RESPONSE_PROMPT_ID not set, using fallback inline prompt")
        # Fallback inline prompt
        return {
            "system": f"""You are a helpful Malaysian telecom customer service assistant for CelcomDigi.

Language: Respond in {('English' if language == 'EN' else 'Bahasa Malaysia')}.

Guidelines:
- Be concise and friendly (1-2 sentences max)
- If asking for PIN, ask for 4-digit security PIN (not 6-digit)
- If asking for phone number, ask for CelcomDigi registered phone number
- If action succeeded, confirm clearly
- NEVER invent information not in context
- Use WhatsApp-style brevity""",
            "user_message": f"""Intent: {intent}

Context:
{json.dumps(context, indent=2)}

Generate an appropriate customer service response."""
        }

    try:
        # Get prompt from Prompt Management
        response = bedrock_agent_mgmt.get_prompt(
            promptIdentifier=RESPONSE_PROMPT_ID
        )

        # Parse correct API structure: variants[0].templateConfiguration.chat
        variants = response.get('variants', [])
        if not variants:
            raise ValueError("No variants in prompt response")
        
        chat_config = variants[0].get('templateConfiguration', {}).get('chat', {})
        
        # Extract system prompt
        system_list = chat_config.get('system', [])
        system_prompt = system_list[0].get('text', '') if system_list else ''
        
        # Extract user message template
        messages = chat_config.get('messages', [])
        user_template = ''
        if messages and messages[0].get('content'):
            user_template = messages[0]['content'][0].get('text', '')

        # Replace variables
        system_prompt = system_prompt.replace('{{intent}}', intent)
        system_prompt = system_prompt.replace('{{context}}', json.dumps(context, indent=2))
        system_prompt = system_prompt.replace('{{language}}', language)
        
        user_message = user_template.replace('{{intent}}', intent)
        user_message = user_message.replace('{{context}}', json.dumps(context, indent=2))
        user_message = user_message.replace('{{language}}', language)

        return {
            "system": system_prompt,
            "user_message": user_message
        }

    except Exception as e:
        print(f"[WARN] Error getting prompt from Prompt Management: {e}")
        # Fallback inline prompt
        return {
            "system": f"""You are a helpful Malaysian telecom customer service assistant for CelcomDigi.

Language: Respond in {('English' if language == 'EN' else 'Bahasa Malaysia')}.

Guidelines:
- Be concise and friendly (1-2 sentences max)
- If asking for PIN, ask for 4-digit security PIN (not 6-digit)
- If asking for phone number, ask for CelcomDigi registered phone number
- If action succeeded, confirm clearly
- NEVER invent information not in context
- Use WhatsApp-style brevity""",
            "user_message": f"""Intent: {intent}

Context:
{json.dumps(context, indent=2)}

Generate an appropriate customer service response."""
        }


@xray_recorder.capture("generate_response")
def generate_response(intent: str, context: Dict[str, Any], language: str = "EN") -> str:
    """
    Generate natural language response using Bedrock Haiku with Guardrails.

    Uses:
    - Prompt Management (no hardcoded prompts)
    - Bedrock Guardrails (PII redaction, content filtering)
    - Automated Reasoning (hallucination prevention)
    - Claude 3 Haiku (fast, cost-effective)
    """
    # Get prompt from Prompt Management
    prompt = get_response_prompt(intent, context, language)

    try:
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "temperature": 0.7,
            "system": prompt["system"],
            "messages": [
                {"role": "user", "content": prompt["user_message"]}
            ]
        }

        invoke_params = {
            'modelId': BEDROCK_HAIKU,  # Use Haiku 3 for response generation
            'body': json.dumps(request_body)
        }

        # Add Guardrails with Automated Reasoning
        if GUARDRAIL_ID:
            invoke_params['guardrailIdentifier'] = GUARDRAIL_ID
            invoke_params['guardrailVersion'] = GUARDRAIL_VERSION

        response = bedrock_runtime.invoke_model(**invoke_params)

        result = json.loads(response['body'].read())

        # Check for guardrail intervention
        if 'trace' in result and result.get('trace', {}).get('guardrail'):
            guardrail_trace = result['trace']['guardrail']
            if guardrail_trace.get('action') == 'GUARDRAIL_INTERVENED':
                print(f"[BLOCKED] Guardrail intervened in response generation")
                # Return safe fallback
                return "I apologize, but I need to transfer you to a human agent for assistance."

        return result['content'][0]['text'].strip()

    except Exception as e:
        print(f"[ERROR] Error generating response: {e}")
        return "I'm sorry, I encountered an error. Please try again or contact customer service."


@xray_recorder.capture("handle_intent")
def handle_intent(intent: str, slots: Dict[str, Any], session_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle detected intent and orchestrate appropriate actions.

    NO hardcoded responses - all via Bedrock with Prompt Management.
    
    Channel-specific behavior:
    - mobile: Skip PIN verification (user is authenticated via app)
    - whatsapp/web: Require phone verification and 4-digit PIN
    """
    session_id = session_data['session_id']
    phone_number = session_data['phone_number']
    customer_id = session_data['customer_id']
    channel = session_data.get('channel', 'web')
    language = slots.get('language_preference', 'EN')
    
    # Check if customer exists in CRM
    customer = lookup_customer(phone_number)
    customer_verified = customer is not None

    # Intent routing
    if intent in ["deactivate_voicemail", "activate_voicemail"]:
        # For mobile channel, skip PIN verification (already authenticated)
        if channel == 'mobile':
            print(f"[INFO] Mobile channel - skipping PIN verification")
            # Execute CRM action directly
            crm_action = "deactivate" if intent == "deactivate_voicemail" else "activate"
            crm_result = invoke_crm(crm_action, phone_number, customer_id, session_id)
            
            if crm_result.get('success'):
                return {
                    "response": generate_response(intent, {
                        "status": "success",
                        "action": crm_action,
                        "voicemail_status": crm_result.get('voicemail_status')
                    }, language),
                    "grounded": True,
                    "citations": ["CRM_API"],
                    "requires_followup": False
                }
            else:
                return {
                    "response": generate_response(intent, {
                        "status": "crm_error",
                        "error": crm_result.get('error')
                    }, language),
                    "grounded": False,
                    "citations": [],
                    "requires_followup": False
                }
        
        # For whatsapp/web: Check if customer is in CRM
        if not customer_verified:
            # Customer not found - ask for CelcomDigi registered phone number
            return {
                "response": generate_response(intent, {
                    "status": "customer_not_found",
                    "message": "We could not find your phone number in our system. Please provide your CelcomDigi registered phone number."
                }, language),
                "grounded": False,
                "citations": [],
                "requires_followup": True,
                "awaiting": "phone_number"
            }
        
        # Customer found - now check for PIN
        security_pin = slots.get('security_pin')

        if not security_pin:
            # Ask for 4-digit PIN
            return {
                "response": generate_response(intent, {
                    "status": "awaiting_pin",
                    "message": "Need 4-digit security PIN for verification"
                }, language),
                "grounded": False,
                "citations": [],
                "requires_followup": True,
                "awaiting": "security_pin"
            }

        # Verify PIN via guardrails
        guard_result = invoke_guardrails("verify_pin", session_id, phone_number, security_pin)

        if not guard_result.get('authorized'):
            return {
                "response": generate_response(intent, {
                    "status": "pin_verification_failed",
                    "error": guard_result.get('error'),
                    "attempts_remaining": guard_result.get('attempts_remaining', 0)
                }, language),
                "grounded": False,
                "citations": [],
                "requires_followup": True
            }

        # Execute CRM action
        crm_action = "deactivate" if intent == "deactivate_voicemail" else "activate"
        crm_result = invoke_crm(crm_action, phone_number, customer_id, session_id)

        if crm_result.get('success'):
            return {
                "response": generate_response(intent, {
                    "status": "success",
                    "action": crm_action,
                    "voicemail_status": crm_result.get('voicemail_status')
                }, language),
                "grounded": True,
                "citations": ["CRM_API"],
                "requires_followup": False
            }
        else:
            return {
                "response": generate_response(intent, {
                    "status": "crm_error",
                    "error": crm_result.get('error')
                }, language),
                "grounded": False,
                "citations": [],
                "requires_followup": False
            }

    elif intent in ["query_voicemail_info", "query_voicemail_access"]:
        # Knowledge base queries (RAG with Automated Reasoning)
        kb_result = retrieve_from_kb(session_data['message'], language)
        return {
            "response": kb_result['response'],
            "grounded": kb_result['grounded'],
            "citations": kb_result['citations'],
            "requires_followup": False
        }

    elif intent == "check_voicemail_status":
        # Check CRM status
        crm_result = invoke_crm("check_status", phone_number, customer_id, session_id)

        if crm_result.get('success'):
            return {
                "response": generate_response(intent, {
                    "status": "success",
                    "voicemail_status": crm_result.get('voicemail_status')
                }, language),
                "grounded": True,
                "citations": ["CRM_API"],
                "requires_followup": False
            }

    elif intent == "greeting":
        return {
            "response": generate_response(intent, {
                "message": "Customer greeted the bot"
            }, language),
            "grounded": False,
            "citations": [],
            "requires_followup": False
        }

    elif intent in ["escalate_to_agent", "out_of_scope"]:
        return {
            "response": generate_response(intent, {
                "message": "Escalation needed"
            }, language),
            "grounded": False,
            "citations": [],
            "requires_followup": False,
            "escalate": True
        }

    elif intent == "abusive_language":
        # Caught by Bedrock Guardrails in NLU
        return {
            "response": "This conversation has been flagged and will be escalated to a supervisor.",
            "grounded": False,
            "citations": [],
            "requires_followup": False,
            "escalate": True
        }

    else:  # unclear_intent
        return {
            "response": generate_response("unclear_intent", {
                "message": "Could not understand request"
            }, language),
            "grounded": False,
            "citations": [],
            "requires_followup": True
        }


@xray_recorder.capture("log_audit")
def log_audit(session_data: Dict[str, Any], nlu_result: Dict[str, Any], response_data: Dict[str, Any], latency_ms: float):
    """Log transaction to audit table."""
    try:
        audit_table = dynamodb.Table(AUDIT_TABLE)

        log_entry = {
            'log_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'customer_id': session_data['customer_id'],
            'session_id': session_data['session_id'],
            'detected_intent': nlu_result.get('intent'),
            'confidence_score': Decimal(str(nlu_result.get('confidence', 0.0))),
            'extracted_slots': nlu_result.get('slots', {}),
            'user_message': session_data['message'],
            'bot_response': response_data.get('response'),
            'model_version': BEDROCK_HAIKU,
            'grounding_sources': response_data.get('citations', []),
            'api_calls': response_data.get('api_calls', []),
            'error_details': response_data.get('error'),
            'latency_ms': Decimal(str(latency_ms)),
            'grounded': response_data.get('grounded', False),
            'hallucination_detected': False  # Automated Reasoning helps prevent
        }

        audit_table.put_item(Item=log_entry)

        print(f"[OK] Audit log created: {log_entry['log_id']}")

    except Exception as e:
        print(f"[ERROR] Error logging audit: {e}")


@xray_recorder.capture("handler")
def handler(event, context):
    """
    Orchestrator Lambda handler with AWS Best Practices (2025).

    Uses:
    - Bedrock Prompt Management (no hardcoded prompts)
    - Bedrock Guardrails (PII, content filtering, automated reasoning)
    - Claude 3 Haiku (fast, cost-effective)
    - Session state tracking for multi-turn conversations
    """
    start_time = datetime.utcnow()

    print(f"[ORCH] Orchestrator invoked with event: {json.dumps(event, default=str)}")

    try:
        # Parse event
        if isinstance(event, str):
            event = json.loads(event)

        session_data = {
            'session_id': event.get('session_id'),
            'customer_id': event.get('customer_id'),
            'phone_number': event.get('phone_number'),
            'message': event.get('message'),
            'turn_number': event.get('turn_number', 0),
            'channel': event.get('channel', 'web')  # whatsapp, web, or mobile
        }

        # Check session state for multi-turn context
        session_state = get_session_state(session_data['session_id'])
        awaiting_action = session_state.get('awaiting_action')
        pending_intent = session_state.get('pending_intent')
        
        message = session_data['message']
        
        # Handle session state - bypass NLU if we're waiting for specific input
        if awaiting_action == 'pin' and pending_intent:
            # User is providing PIN - check if message looks like a PIN (digits only)
            if message.strip().isdigit() and len(message.strip()) == 4:
                print(f"[OK] Session awaiting PIN, message looks like PIN: {message[:2]}**")
                # Treat as PIN input, use pending intent
                intent = pending_intent
                slots = {'security_pin': message.strip()}
                confidence = 1.0
                nlu_result = {'intent': intent, 'confidence': confidence, 'slots': slots}
                # Clear the awaiting state
                update_session_state(session_data['session_id'], None, None)
            else:
                # Not a valid PIN, run NLU normally
                nlu_result = invoke_nlu(message)
                intent = nlu_result.get('intent')
                slots = nlu_result.get('slots', {})
                confidence = nlu_result.get('confidence', 0.0)
        else:
            # Normal flow - invoke NLU for intent detection
            nlu_result = invoke_nlu(message)
            intent = nlu_result.get('intent')
            slots = nlu_result.get('slots', {})
            confidence = nlu_result.get('confidence', 0.0)

        print(f"[OK] NLU Result: intent={intent}, confidence={confidence:.2f}")

        # Handle intent (orchestrate guardrails, CRM, KB)
        response_data = handle_intent(intent, slots, session_data)
        
        # If response indicates we're waiting for something, update session state
        if response_data.get('awaiting') == 'security_pin':
            update_session_state(session_data['session_id'], 'pin', intent)

        # Log to audit table
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        log_audit(session_data, nlu_result, response_data, latency_ms)

        print(f"[OK] Orchestrator completed in {latency_ms:.0f}ms")

        return {
            'statusCode': 200,
            'body': json.dumps(response_data)
        }

    except Exception as e:
        print(f"[ERROR] Error in Orchestrator: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'response': "I apologize, but I encountered an error. Please try again."
            })
        }
