#!/usr/bin/env bash
set -euo pipefail

INPUT="tests/data/NOM_92628.nxs.h5"
OUTPUT=$(mktemp /tmp/shrinkevent_systest_XXXXXX.nxs.h5)
trap 'rm -f "$OUTPUT"' EXIT

echo "Running: pixi run shrinkevent $INPUT $OUTPUT --limit-events 100 --limit-logs 10"
pixi run shrinkevent "$INPUT" "$OUTPUT" --limit-events 100 --limit-logs 10

if [ ! -f "$OUTPUT" ]; then
    echo "FAIL: output file was not created"
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
