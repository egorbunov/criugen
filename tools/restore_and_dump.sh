#! /bin/bash

RESTORED_ROOT_PID=${1}
INPUT_DUMP_DIR=${2}
OUTPUT_NEW_DUMP_DIR=${3}
OUTPUT_NEW_JSONDUMP_DIR=${3}json
CR_TO_JSON_BIN=$(dirname ${0})/crtojson.sh

if [ -z "$RESTORED_ROOT_PID" -o -z "$INPUT_DUMP_DIR" -o -z "$OUTPUT_NEW_DUMP_DIR" ]; then
    echo "USAGE: ./restore_and_dump.sh <TREE_ROOT_PID> <INPUT_DUMP_DIR> <OUTPUT_NEW_DUMP_DIR>"
    exit 1
fi

mkdir -p "$OUTPUT_NEW_DUMP_DIR"
mkdir -p "$OUTPUT_NEW_JSONDUMP_DIR"

echo "Restoring, but keepeing stopped..." && \
sudo criu restore -s -d -D "$INPUT_DUMP_DIR" && \
echo "Dumping to $OUTPUT_NEW_DUMP_DIR ..." && \
sudo criu dump -t "$RESTORED_ROOT_PID" -D "$OUTPUT_NEW_DUMP_DIR" && \
echo "Converting to json to dir $OUTPUT_NEW_JSONDUMP_DIR ..." && \
"$CR_TO_JSON_BIN" "$OUTPUT_NEW_DUMP_DIR" "$OUTPUT_NEW_JSONDUMP_DIR"
