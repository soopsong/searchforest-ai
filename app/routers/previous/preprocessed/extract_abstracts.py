#!/usr/bin/env python3
"""
extract_abstracts.py

Reads a JSONL file of paper metadata (with "paper_id" and "abstract" fields)
and writes each abstract into its own `<paper_id>.txt` under the specified directory.
"""
import os
import json
import argparse

def main(input_jsonl: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    count = 0
    with open(input_jsonl, 'r', encoding='utf-8') as fin:
        for line in fin:
            rec = json.loads(line)
            pid = rec.get('paper_id')
            abstract = rec.get('abstract', '').strip()
            if not pid or not abstract:
                continue
            out_path = os.path.join(output_dir, f"{pid}.txt")
            with open(out_path, 'w', encoding='utf-8') as fout:
                fout.write(abstract)
            count += 1
    print(f"Wrote {{count}} abstracts to {{output_dir}}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Extract abstracts from JSONL into individual .txt files"
    )
    parser.add_argument(
        '--input_jsonl', '-i', required=True,
        help="Path to test metadata JSONL file"
    )
    parser.add_argument(
        '--output_dir', '-o', required=True,
        help="Directory where <paper_id>.txt files will be written"
    )
    args = parser.parse_args()
    main(args.input_jsonl, args.output_dir)
