#!/usr/bin/env python3
"""
Evaluate Intent Detection F1 Score using test dataset.

This script invokes the NLU Lambda function with test examples and calculates
the F1 score to verify the target metric of ≥0.85.

Usage:
    python evaluate_intent_f1.py --lambda-arn chatbot-nlu-engine --region ap-southeast-5
"""

import json
import boto3
import argparse
from typing import List, Dict, Tuple
from collections import defaultdict


def calculate_f1_score(y_true: List[str], y_pred: List[str]) -> Dict[str, float]:
    """
    Calculate F1 score metrics.

    Args:
        y_true: True intent labels
        y_pred: Predicted intent labels

    Returns:
        Dictionary with precision, recall, f1 scores
    """
    # Calculate per-class metrics
    class_metrics = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0})

    for true_label, pred_label in zip(y_true, y_pred):
        if true_label == pred_label:
            class_metrics[true_label]['tp'] += 1
        else:
            class_metrics[pred_label]['fp'] += 1
            class_metrics[true_label]['fn'] += 1

    # Calculate per-class F1
    class_f1_scores = {}
    for intent, metrics in class_metrics.items():
        tp = metrics['tp']
        fp = metrics['fp']
        fn = metrics['fn']

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        class_f1_scores[intent] = {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'support': tp + fn
        }

    # Calculate weighted F1 (average weighted by support)
    total_support = sum(m['support'] for m in class_f1_scores.values())
    weighted_f1 = sum(
        m['f1'] * m['support'] for m in class_f1_scores.values()
    ) / total_support if total_support > 0 else 0.0

    return {
        'weighted_f1': weighted_f1,
        'class_metrics': class_f1_scores
    }


def evaluate_nlu(test_data_file: str, lambda_function_name: str, region: str) -> Tuple[float, Dict]:
    """
    Evaluate NLU Lambda function on test dataset.

    Args:
        test_data_file: Path to nlu_training_data.json
        lambda_function_name: Name of NLU Lambda function
        region: AWS region

    Returns:
        Tuple of (weighted_f1_score, detailed_metrics)
    """
    # Initialize Lambda client
    lambda_client = boto3.client('lambda', region_name=region)

    # Load test data
    print(f"Loading test data from {test_data_file}...")
    with open(test_data_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)

    y_true = []
    y_pred = []
    test_count = 0
    error_count = 0

    print(f"\nEvaluating NLU Lambda function: {lambda_function_name}")
    print("=" * 80)

    # Test each intent
    for intent_obj in test_data['intents']:
        intent_name = intent_obj['intent_name']

        # Combine English, BM, and slang examples
        examples = []
        examples.extend(intent_obj.get('examples_en', []))
        examples.extend(intent_obj.get('examples_bm', []))
        examples.extend(intent_obj.get('examples_slang', []))

        print(f"\nTesting intent '{intent_name}' with {len(examples)} examples...")

        for example in examples:
            test_count += 1

            try:
                # Invoke NLU Lambda
                response = lambda_client.invoke(
                    FunctionName=lambda_function_name,
                    InvocationType='RequestResponse',
                    Payload=json.dumps({"message": example})
                )

                # Parse response
                result = json.loads(response['Payload'].read())

                # Check for errors
                if 'errorMessage' in result:
                    print(f"  ❌ Error: {result['errorMessage']}")
                    error_count += 1
                    continue

                predicted_intent = result.get('intent', 'unclear_intent')
                confidence = result.get('confidence', 0.0)

                # Record results
                y_true.append(intent_name)
                y_pred.append(predicted_intent)

                # Show misclassifications
                if predicted_intent != intent_name:
                    print(f"  ❌ Misclassified: '{example[:50]}...'")
                    print(f"     True: {intent_name} | Predicted: {predicted_intent} (conf: {confidence:.2f})")

            except Exception as e:
                print(f"  ❌ Lambda invocation error: {e}")
                error_count += 1

    # Calculate F1 score
    print("\n" + "=" * 80)
    print(f"Total tests: {test_count} | Errors: {error_count} | Valid: {len(y_true)}")

    if len(y_true) == 0:
        print("❌ No valid test results. Cannot calculate F1 score.")
        return 0.0, {}

    metrics = calculate_f1_score(y_true, y_pred)

    # Display results
    print("\n" + "=" * 80)
    print("EVALUATION RESULTS")
    print("=" * 80)

    print(f"\n✅ Weighted F1 Score: {metrics['weighted_f1']:.4f} (Target: ≥0.85)")

    if metrics['weighted_f1'] >= 0.85:
        print("🎉 SUCCESS: Met target F1 score!")
    else:
        print(f"⚠️  BELOW TARGET: Need to improve by {0.85 - metrics['weighted_f1']:.4f}")

    print("\nPer-Intent Metrics:")
    print("-" * 80)
    print(f"{'Intent':<25} {'Precision':<12} {'Recall':<12} {'F1':<12} {'Support':<10}")
    print("-" * 80)

    for intent, m in sorted(metrics['class_metrics'].items(), key=lambda x: x[1]['f1']):
        print(f"{intent:<25} {m['precision']:>11.4f} {m['recall']:>11.4f} {m['f1']:>11.4f} {m['support']:>9}")

    return metrics['weighted_f1'], metrics


def main():
    parser = argparse.ArgumentParser(description='Evaluate Intent F1 Score')
    parser.add_argument(
        '--test-data',
        default='Data/nlu_training_data.json',
        help='Path to nlu_training_data.json (default: Data/nlu_training_data.json)'
    )
    parser.add_argument(
        '--lambda-arn',
        required=True,
        help='Name or ARN of NLU Lambda function (e.g., chatbot-nlu-engine)'
    )
    parser.add_argument(
        '--region',
        default='ap-southeast-5',
        help='AWS region (default: ap-southeast-5)'
    )
    parser.add_argument(
        '--output',
        help='Output file for detailed metrics (JSON)'
    )

    args = parser.parse_args()

    # Verify file exists
    if not os.path.exists(args.test_data):
        print(f"❌ Error: File not found: {args.test_data}")
        return

    # Evaluate
    f1_score, metrics = evaluate_nlu(args.test_data, args.lambda_arn, args.region)

    # Save detailed metrics if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                'weighted_f1': f1_score,
                'metrics': metrics,
                'target': 0.85,
                'meets_target': f1_score >= 0.85
            }, f, indent=2)
        print(f"\n📊 Detailed metrics saved to: {args.output}")


if __name__ == '__main__':
    import os
    main()
