CRIU_DIR=~/dev/criu
SOURCE_OUT=./src/proto
HEADER_OUT=./include/proto

rm -rf "$SOURCE_OUT" && \
rm -rf "$HEADER_OUT" && \
mkdir -p "$SOURCE_OUT" && \
mkdir -p "$HEADER_OUT"

declare -a PROTOS=("opts" \
	           "core-x86" \
	           "core-arm" \
	           "core-aarch64" \
	           "core-ppc64" \
	           "rlimit" \
	           "timer" \
	           "creds" \
	           "siginfo" \
	           "fown" \
	           "pstree" \
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

mv ${SOURCE_OUT}/*.h ${HEADER_OUT} && \
find ${SOURCE_OUT} -name "*.cc" -print0 | \
	xargs -i@ -0 bash -c 'FILE=@; mv "$FILE" "${FILE%.*}.cpp"' && \
echo OK
