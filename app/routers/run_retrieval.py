#!/usr/bin/env python3
"""
run_retrieval.py

Reads a FAISS index and ID map, then for each paper in a test .jsonl file,
uses the VectorKeywordSearcher to retrieve the top-K most similar paper IDs.
Outputs a JSON mapping from paper_id to list of retrieved IDs.
"""
import json
import argparse
from searcher import VectorKeywordSearcher


def main():
    parser = argparse.ArgumentParser(
        description="Run FAISS retrieval over a test set and save results as JSON"
    )
    parser.add_argument(
        "--index", required=True,
        help="Path to FAISS index file (e.g., paper.index)"
    )
    parser.add_argument(
        "--id_map", required=True,
        help="Path to ID map file (one paper_id per line)"
    )
    parser.add_argument(
        "--test", required=True,
        help="Path to test metadata .jsonl file; each line must have 'paper_id' and 'abstract'"
    )
    parser.add_argument(
        "--topk", type=int, default=5,
        help="Number of top results to retrieve per query"
    )
    parser.add_argument(
        "--model", default="moka-ai/m3e-base",
        help="m3e"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to output JSON file mapping paper_id -> [retrieved_ids]"
    )
    args = parser.parse_args()

    # Initialize the FAISS searcher
    searcher = VectorKeywordSearcher(
        hf_model_name=args.model,
        index_path=args.index,
        id_map_path=args.id_map
    )

    results = {}
    # Read the test file line-by-line
    with open(args.test, 'r', encoding='utf-8') as fin:
        for line in fin:
            rec = json.loads(line)
            pid = rec.get('paper_id')
            query_text = rec.get('abstract', '')
            if pid is None or not query_text:
                continue
            # Retrieve top-k candidates
            hits = [pid for pid, _ in searcher.search(query_text, args.topk)]
            results[pid] = hits

    # Save results to JSON
    with open(args.output, 'w', encoding='utf-8') as fout:
        json.dump(results, fout, indent=2, ensure_ascii=False)

    print(f"Saved retrieval results for {len(results)} queries to {args.output}")


if __name__ == '__main__':
    main()
