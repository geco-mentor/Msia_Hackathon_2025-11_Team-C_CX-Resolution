#!/usr/bin/env python3
"""
Hash Customer PINs in DynamoDB

This script updates existing customer records in DynamoDB with hashed PINs.
It reads plaintext PINs from the source JSON and adds:
- security_pin_hash: PBKDF2-HMAC-SHA256 hashed PIN
- salt: Random salt used for hashing

USAGE:
    python hash_customer_pins.py [--dry-run]

Options:
    --dry-run    Show what would be updated without making changes
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

# Paths
PROJECT_ROOT = "/Users/kita/Desktop/BreakIntoAI/Let-It-Fly"
CUSTOMER_JSON_PATH = os.path.join(PROJECT_ROOT, "Data", "customer_data.json")


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
        100000  # 100,000 iterations (matches Guardrails Lambda)
    )
    return pin_hash.hex()


def load_pin_mapping() -> dict:
    """Load phone_number -> PIN mapping from JSON."""
    try:
        with open(CUSTOMER_JSON_PATH, 'r', encoding='utf-8') as f:
            customers = json.load(f)
        return {c['phone_number']: c.get('security_pin') for c in customers}
    except FileNotFoundError:
        print(f"[ERROR] Error: {CUSTOMER_JSON_PATH} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Error parsing JSON: {e}")
        sys.exit(1)


def hash_customer_pins(dry_run: bool = False):
    """
    Update all customer records with hashed PINs.
    
    Args:
        dry_run: If True, show what would be updated without making changes
    """
    print(f"{'[DRY-RUN] ' if dry_run else ''}Hashing customer PINs in DynamoDB...")
    print(f"   Table: {TABLE_NAME}")
    print(f"   Region: {REGION}")
    print()
    
    # Load PIN mapping from JSON
    pin_mapping = load_pin_mapping()
    print(f"[INFO] Loaded {len(pin_mapping)} PINs from {CUSTOMER_JSON_PATH}")
    print()
    
    # Connect to DynamoDB
    try:
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(TABLE_NAME)
        
        # Check if table exists
        table.load()
        print(f"[OK] Connected to DynamoDB table: {TABLE_NAME}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"[ERROR] Table '{TABLE_NAME}' does not exist!")
            print(f"   Run load_customer_data.py first to create the table and load data.")
            sys.exit(1)
        raise
    except Exception as e:
        print(f"[ERROR] Error connecting to DynamoDB: {e}")
        sys.exit(1)
    
    # Scan all customers
    print(f"\n[INFO] Scanning customers...")
    
    updated_count = 0
    skipped_count = 0
    already_hashed = 0
    not_found = 0
    
    try:
        response = table.scan()
        customers = response.get('Items', [])
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            customers.extend(response.get('Items', []))
        
        print(f"   Found {len(customers)} customers in DynamoDB")
        print()
        
        for customer in customers:
            phone_number = customer.get('phone_number')
            
            if not phone_number:
                print(f"[WARN] Skipping record with no phone_number")
                skipped_count += 1
                continue
            
            # Check if already hashed
            if customer.get('security_pin_hash') and customer.get('salt'):
                print(f"[SKIP] {phone_number}: Already has hashed PIN")
                already_hashed += 1
                continue
            
            # Get plaintext PIN from JSON mapping
            plaintext_pin = pin_mapping.get(phone_number)
            
            if not plaintext_pin:
                print(f"[WARN] {phone_number}: No PIN found in JSON source")
                not_found += 1
                continue
            
            # Generate salt and hash PIN
            salt = os.urandom(32)
            pin_hash = hash_pin(plaintext_pin, salt)
            
            if dry_run:
                print(f"[DRY-RUN] {phone_number}: Would add hash (PIN: {plaintext_pin} → hash: {pin_hash[:16]}...)")
                updated_count += 1
            else:
                # Update DynamoDB record
                try:
                    table.update_item(
                        Key={'phone_number': phone_number},
                        UpdateExpression="SET security_pin_hash = :hash, salt = :salt",
                        ExpressionAttributeValues={
                            ':hash': pin_hash,
                            ':salt': salt.hex()
                        }
                    )
                    print(f"[OK] {phone_number}: Added hashed PIN")
                    updated_count += 1
                except ClientError as e:
                    print(f"[ERROR] {phone_number}: Error updating - {e}")
                    skipped_count += 1
        
    except ClientError as e:
        print(f"[ERROR] Error scanning table: {e}")
        sys.exit(1)
    
    # Summary
    print()
    print("=" * 50)
    print("[SUMMARY]")
    print("=" * 50)
    print(f"   {'Would update' if dry_run else 'Updated'}: {updated_count} customers")
    print(f"   Already hashed: {already_hashed} customers")
    print(f"   PIN not found: {not_found} customers")
    print(f"   Skipped/errors: {skipped_count} customers")
    print()
    
    if dry_run:
        print("[DRY-RUN] This was a DRY RUN. Run without --dry-run to apply changes.")
    else:
        print("[SECURE] All PINs stored as PBKDF2-HMAC-SHA256 hashes (100,000 iterations)")


def verify_hash(phone_number: str, test_pin: str):
    """Verify a PIN against the stored hash."""
    print(f"\n[VERIFY] Verifying PIN for {phone_number}...")
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name=REGION)
        table = dynamodb.Table(TABLE_NAME)
        
        response = table.get_item(Key={'phone_number': phone_number})
        
        if 'Item' not in response:
            print(f"[ERROR] Customer {phone_number} not found")
            return False
        
        customer = response['Item']
        stored_hash = customer.get('security_pin_hash')
        salt_hex = customer.get('salt')
        
        if not stored_hash or not salt_hex:
            print(f"[ERROR] No hash/salt found for {phone_number}")
            return False
        
        # Hash the test PIN with stored salt
        salt = bytes.fromhex(salt_hex)
        computed_hash = hash_pin(test_pin, salt)
        
        if computed_hash == stored_hash:
            print(f"[OK] PIN verified successfully!")
            return True
        else:
            print(f"[ERROR] PIN mismatch")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hash customer PINs in DynamoDB")
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')
    parser.add_argument('--verify', metavar='PHONE', help='Verify PIN for a specific phone number')
    parser.add_argument('--pin', metavar='PIN', help='PIN to verify (use with --verify)')
    
    args = parser.parse_args()
    
    if args.verify:
        if not args.pin:
            print("[ERROR] --pin required with --verify")
            sys.exit(1)
        verify_hash(args.verify, args.pin)
    else:
        hash_customer_pins(dry_run=args.dry_run)

