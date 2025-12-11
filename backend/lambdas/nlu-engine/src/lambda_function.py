"""
NLU Engine Lambda Function - Intent Detection & Slot Extraction

REFACTORED to use AWS Best Practices:
- Bedrock Prompt Management (no hardcoded prompts)
- Bedrock Guardrails (native safety)
- Amazon Nova Pro (primary model)
- Proper error handling

Environment Variables:
    BEDROCK_MODEL_NOVA_PRO or BEDROCK_MODEL: Bedrock model ID (default: apac.amazon.nova-pro-v1:0)
    BEDROCK_GUARDRAIL_ID: Guardrail identifier
    BEDROCK_GUARDRAIL_VERSION: Guardrail version (default: DRAFT)
    NLU_PROMPT_ID: Prompt Management ARN for intent classification
    SLANG_DICT_S3_BUCKET: S3 bucket containing slang_dictionary.json
    SLANG_DICT_S3_KEY: S3 key for slang dictionary
    REGION: AWS region

Input Event:
    {
        "message": "nk off vm skrg",
        "session_id": "SESSION-CUST001-123"
    }

Output:
    {
        "intent": "deactivate_voicemail",
        "confidence": 0.92,
        "slots": {
            "phone_number": "+60123456789",
            "security_pin": null,
            "language_preference": "EN"
        },
        "normalized_message": "nak off voicemail sekarang"
    }
"""

import json
import boto3
from botocore.config import Config
import os
import re
from typing import Dict, Any, Optional
# from aws_xray_sdk.core import xray_recorder  # Removed - not needed for testing

# Initialize AWS clients with retry and timeout config
bedrock_config = Config(
    retries={'max_attempts': 6, 'mode': 'adaptive'},
    connect_timeout=10,
    read_timeout=60,
    max_pool_connections=20
)

bedrock_runtime = boto3.client(
    'bedrock-runtime',
    region_name=os.environ.get('REGION', 'ap-southeast-1'),
    config=bedrock_config
)

bedrock_agent_mgmt = boto3.client(
    'bedrock-agent',
    region_name=os.environ.get('REGION', 'ap-southeast-1')
)

s3_client = boto3.client('s3', region_name=os.environ.get('REGION', 'ap-southeast-1'))

# Global cache for slang dictionary
SLANG_DICT = None

# Configuration
BEDROCK_MODEL = (
    os.environ.get('BEDROCK_MODEL_NOVA_PRO')
    or os.environ.get('BEDROCK_MODEL')
    or os.environ.get('BEDROCK_MODEL_HAIKU')
    or 'apac.amazon.nova-pro-v1:0'
)
GUARDRAIL_ID = os.environ.get('BEDROCK_GUARDRAIL_ID')
GUARDRAIL_VERSION = os.environ.get('BEDROCK_GUARDRAIL_VERSION', 'DRAFT')
NLU_PROMPT_ID = os.environ.get('NLU_PROMPT_ID')  # Prompt Management ARN


def load_slang_dictionary() -> Dict[str, str]:
    """
    Load and FLATTEN nested slang dictionary from S3 (cached globally per Lambda container).

    The S3 file has nested structure: {categories: {common_abbreviations: {entries: [{slang, standard}]}}}
    We flatten it to: {slang_term: standard_term} for fast lookup.

    Returns:
        Dictionary mapping slang terms to normalized forms
    """
    global SLANG_DICT

    if SLANG_DICT is not None:
        return SLANG_DICT

    bucket = os.environ.get('SLANG_DICT_S3_BUCKET')
    key = os.environ.get('SLANG_DICT_S3_KEY', 'slang_dictionary.json')

    if not bucket:
        error_msg = "CRITICAL: SLANG_DICT_S3_BUCKET environment variable not set. Slang normalization DISABLED."
        print(f"[ERROR] {error_msg}")
        raise ValueError(error_msg)  # Fail fast instead of silent fallback

    try:
        print(f"Loading slang dictionary from s3://{bucket}/{key}...")
        response = s3_client.get_object(Bucket=bucket, Key=key)
    except s3_client.exceptions.NoSuchBucket:
        print(f"[ERROR] S3 bucket '{bucket}' does not exist")
        SLANG_DICT = {}
        return SLANG_DICT
    except s3_client.exceptions.NoSuchKey:
        print(f"[ERROR] S3 key '{key}' not found in bucket '{bucket}'")
        SLANG_DICT = {}
        return SLANG_DICT
    except Exception as e:
        error_code = getattr(e.response.get('Error', {}), 'Code', 'Unknown') if hasattr(e, 'response') else 'Unknown'
        if error_code == 'AccessDenied':
            print(f"[ERROR] Access denied to S3 bucket '{bucket}'")
        else:
            print(f"[ERROR] S3 error: {error_code} - {e}")
        SLANG_DICT = {}
        return SLANG_DICT

    try:
        raw_dict = json.loads(response['Body'].read().decode('utf-8'))

        # Flatten nested category structure to simple {slang: standard} mapping
        SLANG_DICT = {}
        for category_name, category_data in raw_dict.get('categories', {}).items():
            entries = category_data.get('entries', [])

            for entry in entries:
                # Handle different entry structures
                if isinstance(entry.get('slang'), str):
                    # Structure 1: {"slang": "nk", "standard": "nak"}
                    slang = entry.get('slang', '').lower()
                    standard = entry.get('standard', slang)
                    if slang:
                        SLANG_DICT[slang] = standard

                elif isinstance(entry.get('slang'), list):
                    # Structure 2: {"slang": ["ape", "mcm mne"], "bahasa": [...], "english": [...]}
                    slang_list = entry.get('slang', [])
                    bahasa_list = entry.get('bahasa', [])
                    english_list = entry.get('english', [])

                    # Map slang to bahasa if available, otherwise to english
                    for idx, slang_term in enumerate(slang_list):
                        if isinstance(slang_term, str):
                            slang_term = slang_term.lower()
                            if idx < len(bahasa_list):
                                SLANG_DICT[slang_term] = bahasa_list[idx]
                            elif idx < len(english_list):
                                SLANG_DICT[slang_term] = english_list[idx]

                elif 'variations' in entry:
                    # Structure 3: action_verbs, service_terms with variations
                    # {"action": "deactivate", "variations": {"english": [...], "bahasa": [...], "slang": [...]}}
                    variations = entry.get('variations', {})
                    slang_list = variations.get('slang', [])
                    bahasa_list = variations.get('bahasa', [])
                    english_list = variations.get('english', [])

                    # Map all slang variations
                    for slang_term in slang_list:
                        if isinstance(slang_term, str):
                            slang_lower = slang_term.lower()
                            # For slang in variations, map to the first bahasa equivalent or first english
                            if bahasa_list:
                                SLANG_DICT[slang_lower] = bahasa_list[0]
                            elif english_list:
                                SLANG_DICT[slang_lower] = english_list[0]

                    # Also map some english/bahasa terms for normalization
                    for eng_term in english_list[:3]:  # Map first few english variations
                        if isinstance(eng_term, str):
                            SLANG_DICT[eng_term.lower()] = eng_term

                    for bm_term in bahasa_list[:3]:  # Map first few bahasa variations
                        if isinstance(bm_term, str):
                            SLANG_DICT[bm_term.lower()] = bm_term

                elif 'english' in entry and 'bahasa' in entry and 'slang' in entry:
                    # Structure 4: question_words, confirmation_words, politeness_markers
                    # {english": [...], "bahasa": [...], "slang": [...]}
                    slang_list = entry.get('slang', [])
                    bahasa_list = entry.get('bahasa', [])

                    # Map slang to corresponding bahasa
                    for idx, slang_term in enumerate(slang_list):
                        if isinstance(slang_term, str):
                            slang_lower = slang_term.lower()
                            if idx < len(bahasa_list):
                                SLANG_DICT[slang_lower] = bahasa_list[idx]

        print(f"[OK] Loaded and flattened {len(SLANG_DICT)} slang mappings from {len(raw_dict.get('categories', {}))} categories")

    except Exception as e:
        print(f"[ERROR] Error loading slang dictionary: {e}")
        SLANG_DICT = {}

    return SLANG_DICT


# @xray_recorder.capture("normalize_slang")  # Removed - not needed
def normalize_slang(message: str) -> str:
    """
    Normalize Malaysian slang in user message.

    Examples:
        "nk off vm skrg" → "nak off voicemail sekarang"
        "pls matikan mel suara" → "please matikan mel suara"

    Args:
        message: User message with potential slang

    Returns:
        Normalized message
    """
    slang_dict = load_slang_dictionary()

    # Tokenize (split on whitespace and keep punctuation)
    tokens = re.findall(r'\w+|[^\w\s]', message.lower())

    normalized_tokens = []
    for token in tokens:
        # Check if token is in slang dictionary
        normalized = slang_dict.get(token, token)
        normalized_tokens.append(normalized)

    return ' '.join(normalized_tokens)


def extract_text_value(text_content) -> str:
    """
    Extract string from Prompt Management text content.
    
    Handles both formats:
    - Direct string: "text here"
    - Dict format: {'format': 'plain_text', 'text': 'text here'}
    - Nested dict: {'text': {'format': 'plain_text', 'text': 'text here'}}
    
    Args:
        text_content: Text content from Prompt Management API
        
    Returns:
        Extracted string value
    """
    if isinstance(text_content, str):
        return text_content
    if isinstance(text_content, dict):
        # Check for nested 'text' field that might be a dict
        text_value = text_content.get('text', '')
        if isinstance(text_value, dict):
            # Handle {'text': {'format': 'plain_text', 'text': 'actual text'}}
            return text_value.get('text', '')
        return text_value if isinstance(text_value, str) else ''
    return ''


# @xray_recorder.capture("get_nlu_prompt")  # Removed - not needed
def get_nlu_prompt(message: str, normalized_message: str) -> Dict[str, Any]:
    """
    Get intent classification prompt from Bedrock Prompt Management.

    Args:
        message: Original user message
        normalized_message: Slang-normalized message

    Returns:
        Prompt with variables substituted
    """
    if not NLU_PROMPT_ID:
        print("[ERROR] NLU_PROMPT_ID not set - Bedrock Prompt Management is required")
        raise ValueError("NLU_PROMPT_ID environment variable must be set to use Bedrock Prompt Management")

    try:
        # Get prompt from Prompt Management
        response = bedrock_agent_mgmt.get_prompt(
            promptIdentifier=NLU_PROMPT_ID
        )

        # Extract prompt content from correct API structure
        # API returns: response['variants'][0]['templateConfiguration']['chat']
        variant = response.get('variants', [{}])[0]
        template_config = variant.get('templateConfiguration', {}).get('chat', {})

        # Get system prompt - use extract_text_value to handle dict format
        system_messages = template_config.get('system', [])
        system_prompt = extract_text_value(system_messages[0]) if system_messages else ''

        # Get user message template - use extract_text_value to handle dict format
        user_messages = template_config.get('messages', [])
        if user_messages:
            content = user_messages[0].get('content', [])
            user_template = extract_text_value(content[0]) if content else ''
        else:
            user_template = ''

        # Substitute variables ({{variable_name}} syntax)
        user_message = user_template.replace('{{original_message}}', message)
        user_message = user_message.replace('{{normalized_message}}', normalized_message)

        return {
            "system": system_prompt,
            "user_message": user_message
        }

    except Exception as e:
        print(f"[ERROR] Error getting prompt from Bedrock Prompt Management: {e}")
        import traceback
        traceback.print_exc()
        # Re-raise to signal that Prompt Management is required
        raise RuntimeError(f"Failed to get NLU prompt from Bedrock Prompt Management: {e}")


# @xray_recorder.capture("detect_intent_bedrock")  # Removed - not needed
def detect_intent_via_bedrock(message: str, normalized_message: str) -> Dict[str, Any]:
    """
    Detect intent and extract slots using Bedrock with Guardrails.

    Args:
        message: Original user message
        normalized_message: Slang-normalized message

    Returns:
        Dictionary with intent, confidence, and slots
    """
    # Get prompt (from Prompt Management or fallback)
    prompt = get_nlu_prompt(message, normalized_message)

    try:
        # Build messages for Nova conversation
        system_messages = [
            {"text": prompt["system"]}
        ]

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt["user_message"]
                    }
                ]
            }
        ]

        converse_args = {
            "modelId": BEDROCK_MODEL,
            "system": system_messages,
            "messages": messages,
            "inferenceConfig": {
                "maxTokens": 500,
                "temperature": 0.1
            }
        }

        # Add guardrails if configured
        if GUARDRAIL_ID:
            converse_args["guardrailConfig"] = {
                "guardrailIdentifier": GUARDRAIL_ID,
                "guardrailVersion": GUARDRAIL_VERSION
            }

        response = bedrock_runtime.converse(**converse_args)

        content_blocks = response.get("output", {}).get("message", {}).get("content", [])
        if not content_blocks or not content_blocks[0].get("text"):
            raise ValueError("Empty or unexpected content returned from model")

        content_text = content_blocks[0].get("text", "")

        # Extract JSON from response (handle markdown code blocks if present)
        json_match = re.search(r'```(?:json)?\\s*(\\{.*?\\})\\s*```', content_text, re.DOTALL)
        if json_match:
            content_text = json_match.group(1).strip()
        elif '```' in content_text:
            parts = content_text.split('```')
            if len(parts) >= 3:
                content_text = parts[1].strip()
                if content_text.startswith('json'):
                    content_text = content_text[4:].strip()

        intent_result = json.loads(content_text)

        # Validate required fields
        if 'intent' not in intent_result or 'confidence' not in intent_result:
            raise ValueError("Missing required fields in Bedrock response")

        # Ensure slots exist
        if 'slots' not in intent_result:
            intent_result['slots'] = {
                "phone_number": None,
                "security_pin": None,
                "language_preference": "EN"
            }

        print(f"[OK] Intent detected: {intent_result['intent']} (confidence: {intent_result['confidence']:.2f})")

        return intent_result

    except Exception as e:
        print(f"[ERROR] Error calling Bedrock: {e}")
        # Fallback to unclear_intent
        return {
            "intent": "unclear_intent",
            "confidence": 0.0,
            "slots": {
                "phone_number": None,
                "security_pin": None,
                "language_preference": "EN"
            },
            "reasoning": f"Error during intent detection: {str(e)}"
        }


# @xray_recorder.capture("handler")  # Removed - not needed
def handler(event, context):
    """
    Lambda handler for NLU Engine.

    Args:
        event: API Gateway or direct invocation event
        context: Lambda context object

    Returns:
        Intent detection result with slots
    """
    print(f"[NLU] NLU Engine invoked with event: {json.dumps(event)}")

    try:
        # Parse input
        if isinstance(event, str):
            event = json.loads(event)

        # Get message from event
        if 'body' in event:
            # API Gateway event
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            message = body.get('message', '')
        else:
            # Direct Lambda invocation
            message = event.get('message', '')

        if not message:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required field: message'})
            }

        # Step 1: Normalize slang
        print(f"Original message: {message}")
        normalized_message = normalize_slang(message)
        print(f"Normalized message: {normalized_message}")

        # Step 2: Detect intent via Bedrock (with Guardrails)
        result = detect_intent_via_bedrock(message, normalized_message)

        # Step 3: Add normalized message to result
        result['normalized_message'] = normalized_message

        # Return result
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        } if 'body' in event else result

    except Exception as e:
        print(f"[ERROR] Error in NLU Engine: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'intent': 'unclear_intent',
                'confidence': 0.0
            })
        }
