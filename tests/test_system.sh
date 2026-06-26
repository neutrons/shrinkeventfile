#!/usr/bin/env bash
set -euo pipefail

INPUT="tests/data/NOM_92628.nxs.h5"
OUTPUT_DIR=$(mktemp -d /tmp/shrinkevent_systest_XXXXXX)
OUTPUT="$OUTPUT_DIR/output.nxs.h5"
trap 'rm -rf "$OUTPUT_DIR"' EXIT

echo "Running: pixi run -e dev shrinkevent $INPUT $OUTPUT --limit-events 100 --limit-logs 10"
pixi run -e dev shrinkevent "$INPUT" "$OUTPUT" --limit-events 100 --limit-logs 10

if [ ! -s "$OUTPUT" ]; then
    echo "FAIL: output file was not created or is empty"
    exit 1
fi

INPUT_SIZE=$(wc -c < "$INPUT")
OUTPUT_SIZE=$(wc -c < "$OUTPUT")

echo "Input size:  $INPUT_SIZE bytes"
echo "Output size: $OUTPUT_SIZE bytes"

if [ "$OUTPUT_SIZE" -ge "$INPUT_SIZE" ]; then
    echo "FAIL: output is not smaller than input"
    exit 1
fi

echo "PASS"
