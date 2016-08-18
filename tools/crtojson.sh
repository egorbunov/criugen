#! /bin/bash

INPUT_DIR=${1:-"."}
OUTPUT_DIR=${2:-"./"}
OUTPUT_DIR=${OUTPUT_DIR%/}

mkdir -p "$OUTPUT_DIR"

while read -r -d '' file; do
    base=$(basename "$file")
    outfile=${OUTPUT_DIR}/${base%.*}.json
    crit decode --pretty -i "$file" -o "$outfile"
done < <(find ${INPUT_DIR} -type f -name "*.img" -print0)
