#! /bin/bash
BINDIR=$(pwd)/bin
BIN=$BINDIR/targetproc
LOGFILE=$BINDIR/log.txt
DUMPDIR=$BINDIR/dump
JSONDIR=$BINDIR/jsondump
TOJSONBIN=$(pwd)/../../tools/crtojson.sh

rm -rf ${BINDIR}
mkdir -p ${BINDIR}
rm -rf ${DUMPDIR}
mkdir -p ${DUMPDIR}
rm -rf ${JSONDIR}
mkdir -p ${JSONDIR}

rm $BIN
gcc main.c -o "$BIN"

$BIN "${LOGFILE}" &
sleep 1

PID=$(cat "$LOGFILE" | head -n 1)
cat /proc/${PID}/maps && \
echo "Dumping...${PID}" && \
sudo criu dump -t "$PID" -D "$DUMPDIR" -vvv -o dump.log && \
echo "OK" && \
echo "Converting to json..." && \
"$TOJSONBIN" "$DUMPDIR" "$JSONDIR" && \
echo "OK"
