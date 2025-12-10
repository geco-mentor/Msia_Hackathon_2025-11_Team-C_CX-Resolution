#!/usr/bin/env python3
"""
Convert kb_articles.json to individual text files for Bedrock Knowledge Base.

This script reads the KB articles JSON and creates separate text files
for English and Bahasa Malaysia versions.
"""

import json
import os
import sys

def main():
    # Paths
    project_root = "/Users/kita/Desktop/BreakIntoAI/Let-It-Fly"
    kb_json_path = os.path.join(project_root, "Data", "kb_articles.json")
    output_dir = os.path.join(project_root, "kb_articles_converted")

    # Create output directories
    os.makedirs(os.path.join(output_dir, "en"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "bm"), exist_ok=True)

    # Load KB articles
    try:
        with open(kb_json_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Error: {kb_json_path} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Error parsing JSON: {e}")
        sys.exit(1)

    # Convert each article
    converted_count = 0
    for article in articles:
        article_id = article.get('id', f'ARTICLE{converted_count}')

        # English version
        en_content = f"""Title: {article.get('title_en', 'Untitled')}
Category: {article.get('category', 'general')}

{article.get('content_en', 'No content available')}
"""
        en_file = os.path.join(output_dir, "en", f"{article_id}-en.txt")
        with open(en_file, 'w', encoding='utf-8') as f:
            f.write(en_content)

        # Bahasa Malaysia version
        bm_content = f"""Tajuk: {article.get('title_bm', 'Tiada tajuk')}
Kategori: {article.get('category', 'umum')}

{article.get('content_bm', 'Tiada kandungan')}
"""
        bm_file = os.path.join(output_dir, "bm", f"{article_id}-bm.txt")
        with open(bm_file, 'w', encoding='utf-8') as f:
            f.write(bm_content)

        converted_count += 1

    print(f"[OK] Converted {converted_count} articles to S3 format")
    print(f"   Output directory: {output_dir}")
    print(f"   English files: {os.path.join(output_dir, 'en')}")
    print(f"   Bahasa Malaysia files: {os.path.join(output_dir, 'bm')}")

if __name__ == "__main__":
    main()
