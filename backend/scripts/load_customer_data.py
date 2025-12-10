#!/usr/bin/env python3
"""
Load customer data from JSON into DynamoDB with secure PIN hashing.

SECURITY: Never stores plaintext PINs - uses PBKDF2-HMAC-SHA256 with salt.
"""

import json
import os
import sys
import hashlib
import boto3
from botocore.exceptions import ClientError

# AWS Configuration
REGION = 'ap-southeast-1'
TABLE_NAME = 'chatbot-customers'

def hash_pin(pin: str, salt: bytes) -> str:
    """
    Hash PIN using PBKDF2-HMAC-SHA256.

    Args:
        pin: Plaintext PIN (4 digits)
        salt: Random salt bytes

    Returns:
        Hex string of hashed PIN
    """
    pin_hash = hashlib.pbkdf2_hmac(
        'sha256',
        pin.encode('utf-8'),
        salt,
        100000  # 100,000 iterations
    )
    return pin_hash.hex()

def load_customer_data():
    """Load customer data from JSON and insert into DynamoDB with hashed PINs."""

    # Paths
    project_root = "/Users/kita/Desktop/BreakIntoAI/Let-It-Fly"
    customer_json_path = os.path.join(project_root, "Data", "customer_data.json")

    # Load customer data
    try:
        with open(customer_json_path, 'r', encoding='utf-8') as f:
            customers = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Error: {customer_json_path} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Error parsing JSON: {e}")
        sys.exit(1)

    # Initialize DynamoDB client
    try:
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(TABLE_NAME)
    except Exception as e:
        print(f"[ERROR] Error connecting to DynamoDB: {e}")
        sys.exit(1)

    # Load each customer
    loaded_count = 0
    skipped_count = 0

    for customer in customers:
        phone_number = customer.get('phone_number')
        plaintext_pin = customer.get('security_pin')

        if not phone_number or not plaintext_pin:
            print(f"[WARN] Skipping customer with missing phone_number or PIN")
            skipped_count += 1
            continue

        # Generate random salt for this customer
        salt = os.urandom(32)

        # Hash the PIN
        pin_hash = hash_pin(plaintext_pin, salt)

        # Prepare customer record (remove plaintext PIN)
        customer_record = {
            'phone_number': phone_number,
            'customer_id': customer.get('customer_id', phone_number),
            'name': customer.get('name', 'Unknown'),
            'language_preference': customer.get('language_preference', 'EN'),
            'voicemail_active': customer.get('voicemail_active', False),
            'security_pin_hash': pin_hash,
            'salt': salt.hex(),
            'created_at': customer.get('created_at', '2024-01-01T00:00:00Z')
        }

        # Insert into DynamoDB
        try:
            table.put_item(Item=customer_record)
            loaded_count += 1
            print(f"[OK] Loaded customer: {phone_number} ({customer.get('name', 'Unknown')})")
        except ClientError as e:
            print(f"[ERROR] Error loading {phone_number}: {e}")
            skipped_count += 1

    print(f"\n[SUMMARY] Summary:")
    print(f"   Loaded: {loaded_count} customers")
    print(f"   Skipped: {skipped_count} customers")
    print(f"   Total: {len(customers)} customers in source file")
    print(f"\n[SECURE] Security: All PINs stored as PBKDF2-HMAC-SHA256 hashes (100,000 iterations)")

if __name__ == "__main__":
    load_customer_data()
