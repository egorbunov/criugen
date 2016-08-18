CRIU_DIR=~/dev/criu
SOURCE_OUT=./src/proto
HEADER_OUT=./include/proto

mkdir -p "$SOURCE_OUT" && \
mkdir -p "$HEADER_OUT"

declare -a PROTOS=("pstree" \
	           "fs" \
	           "fdinfo" \
	           "core" \
	           "mm" \
	           "regfile" \
	           "inventory" \
	           "vma")

echo "Generating C++ bindings for proto files: ${PROTOS[@]}"
for f in "${PROTOS[@]}"; do
	protoc -I=${CRIU_DIR}/images --cpp_out="$SOURCE_OUT" ${CRIU_DIR}/images/${f}.proto
done

mv ${SOURCE_OUT}/*.h ${HEADER_OUT}