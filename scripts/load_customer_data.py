#!/usr/bin/env python3
"""
Load customer data from JSON into DynamoDB with secure PIN hashing.

SECURITY: NEVER store plaintext PINs. Always use PBKDF2 with salt.

Usage:
    python load_customer_data.py --region ap-southeast-5
"""

import json
import boto3
import hashlib
import os
import argparse
from datetime import datetime


def hash_pin(pin: str, salt: bytes) -> str:
    """
    Hash PIN using PBKDF2-HMAC-SHA256 with 100,000 iterations.

    Args:
        pin: Plaintext 4-digit PIN
        salt: Random 32-byte salt

    Returns:
        Hex-encoded hash
    """
    pin_hash = hashlib.pbkdf2_hmac(
        'sha256',
        pin.encode('utf-8'),
        salt,
        100000  # Iterations
    )
    return pin_hash.hex()


def load_customers(data_file: str, table_name: str, region: str):
    """
    Load customer data from JSON file into DynamoDB.

    Args:
        data_file: Path to customer_data.json
        table_name: DynamoDB table name
        region: AWS region
    """
    # Initialize DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)

    # Load customer data
    print(f"Loading customer data from {data_file}...")
    with open(data_file, 'r') as f:
        customers = json.load(f)

    print(f"Found {len(customers)} customers")

    # Process each customer
    loaded_count = 0
    for customer in customers:
        # Generate random salt for PIN hashing
        salt = os.urandom(32)

        # Hash the PIN (NEVER store plaintext)
        plaintext_pin = customer.get('security_pin', '')
        if not plaintext_pin:
            print(f"⚠️  Warning: Customer {customer.get('customer_id')} has no PIN")
            continue

        pin_hash = hash_pin(plaintext_pin, salt)

        # Remove plaintext PIN from customer data
        del customer['security_pin']

        # Add hashed PIN and salt
        customer['security_pin_hash'] = pin_hash
        customer['salt'] = salt.hex()

        # Add metadata
        customer['created_at'] = customer.get('created_at', datetime.utcnow().isoformat())
        customer['updated_at'] = datetime.utcnow().isoformat()

        # Ensure pin_locked_until is null (not locked)
        customer['pin_locked_until'] = None

        # Insert into DynamoDB
        try:
            table.put_item(Item=customer)
            loaded_count += 1
            print(f"✅ Loaded customer: {customer['customer_id']} ({customer['phone_number']})")
        except Exception as e:
            print(f"❌ Error loading customer {customer.get('customer_id')}: {e}")

    print(f"\n✅ Successfully loaded {loaded_count}/{len(customers)} customers into DynamoDB table '{table_name}'")
    print(f"⚠️  SECURITY: All PINs are hashed with PBKDF2-SHA256. Plaintext PINs are NOT stored.")


def main():
    parser = argparse.ArgumentParser(description='Load customer data into DynamoDB')
    parser.add_argument(
        '--data-file',
        default='Data/customer_data.json',
        help='Path to customer_data.json (default: Data/customer_data.json)'
    )
    parser.add_argument(
        '--table-name',
        default='chatbot-customers',
        help='DynamoDB table name (default: chatbot-customers)'
    )
    parser.add_argument(
        '--region',
        default='ap-southeast-5',
        help='AWS region (default: ap-southeast-5)'
    )

    args = parser.parse_args()

    # Verify file exists
    if not os.path.exists(args.data_file):
        print(f"❌ Error: File not found: {args.data_file}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Expected file at: {os.path.abspath(args.data_file)}")
        return

    load_customers(args.data_file, args.table_name, args.region)


if __name__ == '__main__':
    main()
