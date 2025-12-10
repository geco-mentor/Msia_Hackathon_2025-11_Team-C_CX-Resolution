#!/usr/bin/env python3
"""
Convert kb_articles.json to individual text files for Amazon Bedrock Knowledge Base.

Bedrock Knowledge Bases require text files (not JSON) for ingestion.
This script creates separate files for English and Bahasa Malaysia content.

Usage:
    python convert_kb_to_s3_format.py --output-dir kb_articles_converted
"""

import json
import os
import argparse


def convert_kb_articles(kb_file: str, output_dir: str):
    """
    Convert KB articles from JSON to individual text files.

    Args:
        kb_file: Path to kb_articles.json
        output_dir: Output directory for converted files
    """
    # Create output directories
    en_dir = os.path.join(output_dir, 'en')
    bm_dir = os.path.join(output_dir, 'bm')
    os.makedirs(en_dir, exist_ok=True)
    os.makedirs(bm_dir, exist_ok=True)

    print(f"Loading KB articles from {kb_file}...")
    with open(kb_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    print(f"Found {len(articles)} articles")
    print(f"Output directory: {output_dir}")

    # Process each article
    for article in articles:
        article_id = article['id']

        # Extract keywords if present
        keywords_en = article.get('keywords_en', [])
        keywords_bm = article.get('keywords_bm', [])

        # Format English version
        en_content = f"""Title: {article['title_en']}
Article ID: {article_id}
Keywords: {', '.join(keywords_en) if keywords_en else 'N/A'}

{article['content_en']}
"""

        # Format Bahasa Malaysia version
        bm_content = f"""Title: {article['title_bm']}
Article ID: {article_id}
Keywords: {', '.join(keywords_bm) if keywords_bm else 'N/A'}

{article['content_bm']}
"""

        # Write English file
        en_file = os.path.join(en_dir, f"{article_id}-en.txt")
        with open(en_file, 'w', encoding='utf-8') as f:
            f.write(en_content)

        # Write Bahasa Malaysia file
        bm_file = os.path.join(bm_dir, f"{article_id}-bm.txt")
        with open(bm_file, 'w', encoding='utf-8') as f:
            f.write(bm_content)

        print(f"✅ Converted {article_id}: {article['title_en']}")

    print(f"\n✅ Successfully converted {len(articles)} articles")
    print(f"📁 English articles: {en_dir}/")
    print(f"📁 Bahasa Malaysia articles: {bm_dir}/")
    print(f"\nNext steps:")
    print(f"  1. Upload to S3:")
    print(f"     aws s3 sync {output_dir}/ s3://chatbot-kb-malaysia-{{AWS_ACCOUNT_ID}}/articles/ --region ap-southeast-5")
    print(f"  2. Create Bedrock Knowledge Base pointing to S3 bucket")
    print(f"  3. Sync the knowledge base to ingest the articles")


def main():
    parser = argparse.ArgumentParser(description='Convert KB articles to S3 format')
    parser.add_argument(
        '--kb-file',
        default='Data/kb_articles.json',
        help='Path to kb_articles.json (default: Data/kb_articles.json)'
    )
    parser.add_argument(
        '--output-dir',
        default='kb_articles_converted',
        help='Output directory (default: kb_articles_converted)'
    )

    args = parser.parse_args()

    # Verify file exists
    if not os.path.exists(args.kb_file):
        print(f"❌ Error: File not found: {args.kb_file}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Expected file at: {os.path.abspath(args.kb_file)}")
        return

    convert_kb_articles(args.kb_file, args.output_dir)


if __name__ == '__main__':
    main()
