#!/usr/bin/env python3
# concat_abstracts.py

import os
import argparse

def main(abstract_dir: str, output_path: str):
    with open(output_path, 'w', encoding='utf-8') as fout:
        for fname in sorted(os.listdir(abstract_dir)):
            if not fname.endswith('.txt'):
                continue
            pid = os.path.splitext(fname)[0]
            path = os.path.join(abstract_dir, fname)
            with open(path, 'r', encoding='utf-8') as fin:
                text = fin.read().strip().replace('\n', ' ')
            if text:
                fout.write(f"{pid}\t{text}\n")
    print(f"[✓] Wrote all abstracts to {output_path!r}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="각 paper_id.txt (abstract)를 한 줄씩 모아 all_abstract.txt 생성"
    )
    p.add_argument(
        "--abstract_dir",
        required=True,
        help="abstract .txt 파일들이 들어있는 디렉터리"
    )
    p.add_argument(
        "--output",
        default="all_abstract.txt",
        help="출력 파일명 (기본: all_abstract.txt)"
    )
    args = p.parse_args()

    main(args.abstract_dir, args.output)
