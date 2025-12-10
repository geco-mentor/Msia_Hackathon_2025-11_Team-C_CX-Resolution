#!/bin/bash

###############################################################################
# Lambda Deployment Script
#
# Deploys all 6 Lambda functions for the multilingual chatbot:
# 1. chatbot-whatsapp-webhook (API Handler for Flutter app)
# 2. chatbot-twilio-webhook (Twilio WhatsApp integration)
# 3. chatbot-orchestrator
# 4. chatbot-nlu-engine
# 5. chatbot-guardrails
# 6. chatbot-crm-mock
#
# Prerequisites:
# - AWS CLI configured with credentials
# - IAM role ChatbotLambdaExecutionRole exists
# - .env.lambda file with environment variables
# - Python 3.12 installed
###############################################################################

set -e  # Exit on error

# Configuration
REGION="ap-southeast-1"
BACKEND_DIR="/Users/kita/Desktop/BreakIntoAI/Let-It-Fly/backend"
ROLE_NAME="ChatbotLambdaExecutionRole"
RUNTIME="python3.12"

# Per-Lambda memory and timeout configurations (optimized for P95 < 2.5s)
declare -A LAMBDA_MEMORY=(
    ["crm-mock"]=256
    ["guardrails"]=512
    ["nlu-engine"]=1024
    ["orchestrator"]=1536
    ["whatsapp-webhook"]=1024
    ["twilio-webhook"]=1024
)

declare -A LAMBDA_TIMEOUT=(
    ["crm-mock"]=10
    ["guardrails"]=10
    ["nlu-engine"]=15
    ["orchestrator"]=30
    ["whatsapp-webhook"]=30
    ["twilio-webhook"]=30
)

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}[INFO] ${1}${NC}"
}

echo_success() {
    echo -e "${GREEN}[OK] ${1}${NC}"
}

echo_warning() {
    echo -e "${YELLOW}[WARN] ${1}${NC}"
}

echo_error() {
    echo -e "${RED}[ERROR] ${1}${NC}"
}

echo_section() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}${1}${NC}"
    echo -e "${BLUE}========================================${NC}"
}

###############################################################################
# Pre-flight Checks
###############################################################################

preflight_checks() {
    echo_section "Pre-flight Checks"

    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo_error "AWS CLI not found. Please install it first."
        exit 1
    fi

    # Check credentials
    if ! aws sts get-caller-identity &>/dev/null; then
        echo_error "AWS credentials not configured. Run 'aws configure'"
        exit 1
    fi

    # Check IAM role exists
    if ! aws iam get-role --role-name $ROLE_NAME &>/dev/null; then
        echo_error "IAM role $ROLE_NAME not found. Run setup_infrastructure.sh first."
        exit 1
    fi

    # Check .env.lambda exists
    if [ ! -f "$BACKEND_DIR/.env.lambda" ]; then
        echo_error ".env.lambda file not found. Please create it first."
        exit 1
    fi

    echo_success "All pre-flight checks passed"
}

###############################################################################
# Load Environment Variables
###############################################################################

load_env_vars() {
    echo_info "Loading environment variables from .env.lambda..."

    # Parse .env.lambda into JSON format for AWS Lambda
    ENV_VARS=$(cat "$BACKEND_DIR/.env.lambda" | grep -v '^#' | grep -v '^$' | awk -F= '{print "\""$1"\":\""$2"\""}' | paste -sd ',' -)
    ENV_VARS_JSON="{\"Variables\":{$ENV_VARS}}"

    echo_success "Environment variables loaded"
}

###############################################################################
# Package Lambda Function
###############################################################################

package_lambda() {
    local LAMBDA_NAME=$1
    local LAMBDA_DIR="$BACKEND_DIR/lambdas/$LAMBDA_NAME"
    local BUILD_DIR="$LAMBDA_DIR/build"
    local ZIP_FILE="$LAMBDA_DIR/function.zip"

    echo_info "Packaging $LAMBDA_NAME..." >&2

    # Clean previous build
    rm -rf "$BUILD_DIR"
    rm -f "$ZIP_FILE"
    mkdir -p "$BUILD_DIR"

    # Copy source code
    cp -r "$LAMBDA_DIR/src/"* "$BUILD_DIR/"

    # Install dependencies if requirements.txt exists
    if [ -f "$LAMBDA_DIR/requirements.txt" ]; then
        echo_info "Installing dependencies for $LAMBDA_NAME..." >&2
        pip3 install -r "$LAMBDA_DIR/requirements.txt" -t "$BUILD_DIR" --quiet --upgrade 2>&1 | grep -v "dependency conflicts" >&2 || true
    fi

    # Create deployment package
    cd "$BUILD_DIR"
    zip -r "$ZIP_FILE" . -q
    cd - > /dev/null

    # Clean build directory
    rm -rf "$BUILD_DIR"

    echo_success "Packaged $LAMBDA_NAME ($(du -h $ZIP_FILE | cut -f1))" >&2

    echo "$ZIP_FILE"
}

###############################################################################
# Deploy Lambda Function
###############################################################################

deploy_lambda() {
    local LAMBDA_NAME=$1
    local ZIP_FILE=$2
    local FUNCTION_NAME="chatbot-${LAMBDA_NAME}"
    
    # Get per-Lambda memory and timeout (with defaults)
    local MEMORY=${LAMBDA_MEMORY[$LAMBDA_NAME]:-512}
    local TIMEOUT=${LAMBDA_TIMEOUT[$LAMBDA_NAME]:-30}

    # Get IAM role ARN
    ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)

    echo_info "Deploying $FUNCTION_NAME (Memory: ${MEMORY}MB, Timeout: ${TIMEOUT}s)..."

    # Check if function exists
    if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION &>/dev/null; then
        # Update existing function
        echo_info "Function exists, updating code..."
        aws lambda update-function-code \
            --function-name $FUNCTION_NAME \
            --zip-file fileb://$ZIP_FILE \
            --region $REGION \
            --no-cli-pager > /dev/null

        # Wait for update to complete
        aws lambda wait function-updated --function-name $FUNCTION_NAME --region $REGION

        # Update configuration
        echo_info "Updating configuration..."
        aws lambda update-function-configuration \
            --function-name $FUNCTION_NAME \
            --runtime $RUNTIME \
            --handler lambda_function.handler \
            --timeout $TIMEOUT \
            --memory-size $MEMORY \
            --environment "$ENV_VARS_JSON" \
            --region $REGION \
            --no-cli-pager > /dev/null

        echo_success "Updated $FUNCTION_NAME"
    else
        # Create new function
        echo_info "Creating new function..."
        aws lambda create-function \
            --function-name $FUNCTION_NAME \
            --runtime $RUNTIME \
            --role $ROLE_ARN \
            --handler lambda_function.handler \
            --zip-file fileb://$ZIP_FILE \
            --timeout $TIMEOUT \
            --memory-size $MEMORY \
            --environment "$ENV_VARS_JSON" \
            --tracing-config Mode=Active \
            --region $REGION \
            --no-cli-pager > /dev/null

        echo_success "Created $FUNCTION_NAME"
    fi

    # Clean up zip file
    rm -f "$ZIP_FILE"
}

###############################################################################
# Main Deployment Flow
###############################################################################

main() {
    echo_section "Lambda Deployment - Multilingual Chatbot"

    # Run pre-flight checks
    preflight_checks

    # Load environment variables
    load_env_vars

    # Define lambdas to deploy (in dependency order)
    LAMBDAS=(
        "crm-mock"
        "guardrails"
        "nlu-engine"
        "orchestrator"
        "whatsapp-webhook"
        "twilio-webhook"
    )

    # Deploy each lambda
    echo_section "Deploying Lambda Functions"

    for LAMBDA in "${LAMBDAS[@]}"; do
        ZIP_FILE=$(package_lambda $LAMBDA)
        deploy_lambda $LAMBDA $ZIP_FILE
    done

    # Verify deployment
    echo_section "Deployment Verification"

    echo_info "Listing deployed functions..."
    aws lambda list-functions \
        --region $REGION \
        --query 'Functions[?starts_with(FunctionName, `chatbot-`)].{Name:FunctionName,Runtime:Runtime,Updated:LastModified}' \
        --output table

    echo ""
    echo_success "All Lambda functions deployed successfully!"
    echo ""
    echo_info "Next steps:"
    echo "  1. Test the NLU engine: aws lambda invoke --function-name chatbot-nlu-engine --payload '{\"message\":\"nk off vm\"}' /tmp/output.json"
    echo "  2. Check CloudWatch Logs for any errors"
    echo "  3. Review audit logs in DynamoDB table: chatbot-audit-logs"
    echo "  4. Create API Gateway when ready to integrate with Flutter app"
}

# Run main function
main
