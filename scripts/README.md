# Helper Scripts

This directory contains utility scripts for setting up and managing the chatbot system.

## Installation

Install Python dependencies:

```bash
cd scripts
pip install -r requirements.txt
```

## Scripts

### 1. `load_customer_data.py`

Load customer data from JSON into DynamoDB with secure PIN hashing.

**SECURITY**: All PINs are hashed using PBKDF2-HMAC-SHA256. Plaintext PINs are NEVER stored.

```bash
python load_customer_data.py \
  --data-file ../Data/customer_data.json \
  --table-name chatbot-customers \
  --region ap-southeast-5
```

### 2. `convert_kb_to_s3_format.py`

Convert knowledge base articles from JSON to individual text files for Bedrock.

```bash
python convert_kb_to_s3_format.py \
  --kb-file ../Data/kb_articles.json \
  --output-dir kb_articles_converted
```

After conversion, upload to S3:

```bash
aws s3 sync kb_articles_converted/ s3://chatbot-kb-malaysia-{ACCOUNT_ID}/articles/ \
  --region ap-southeast-5
```

### 3. `evaluate_intent_f1.py`

Calculate Intent F1 score to verify target metric (≥0.85).

```bash
python evaluate_intent_f1.py \
  --test-data ../Data/nlu_training_data.json \
  --lambda-arn chatbot-nlu-engine \
  --region ap-southeast-5 \
  --output metrics_report.json
```

### 4. `deploy_all_lambdas.sh`

Deploy all 5 Lambda functions in one command.

```bash
./deploy_all_lambdas.sh --region ap-southeast-5
```

## Typical Workflow

1. **Setup AWS Infrastructure** (DynamoDB, S3, Bedrock, IAM, Lambda functions)

2. **Load Initial Data**:
   ```bash
   # Convert KB articles
   python convert_kb_to_s3_format.py

   # Upload to S3
   aws s3 sync kb_articles_converted/ s3://chatbot-kb-malaysia-{ACCOUNT}/articles/ --region ap-southeast-5

   # Load customer data
   python load_customer_data.py
   ```

3. **Deploy Lambda Functions**:
   ```bash
   ./deploy_all_lambdas.sh
   ```

4. **Evaluate Performance**:
   ```bash
   python evaluate_intent_f1.py --lambda-arn chatbot-nlu-engine
   ```

## Security Notes

- **Never commit** `customer_data.json` with plaintext PINs to version control
- All PINs are hashed with 100,000 PBKDF2 iterations
- Each customer has a unique salt for PIN hashing
- Account lockout after 3 failed PIN attempts (15-minute lockout)
