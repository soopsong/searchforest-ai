#!/bin/bash

# 사용법: ./make_tar.sh [압축할 디렉토리] [출력 파일명.tar.gz]

SRC_DIR=$1
OUTPUT_FILE=$2

if [ -z "$SRC_DIR" ] || [ -z "$OUTPUT_FILE" ]; then
  echo "Usage: $0 [source_directory] [output_file.tar.gz]"
  exit 1
fi

tar -czvf "$OUTPUT_FILE" "$SRC_DIR"
echo "Created: $OUTPUT_FILE"