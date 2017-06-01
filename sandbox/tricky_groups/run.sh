#! /bin/bash
BINDIR=$(pwd)/bin
BIN=$BINDIR/tricky_groups
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
gcc main.c -pthread -o "$BIN"

$BIN "${LOGFILE}" &
sleep 1

PID=$(cat "$LOGFILE" | head -n 1)

slept=0
while [ "$(cat "$LOGFILE" | tail -n 2 | tr -d '\n ')" != "FINISH" ]; do 
	sleep 0.1
	slept=$((slept+1))
	if [ $slept -eq 100 ]; then
		break
	fi
done

echo "Dumping...${PID}" && \
sudo criu dump -t "$PID" -D "$DUMPDIR" -vvv -o dump.log && \
echo "OK" && \
echo "Converting to json..." && \
"$TOJSONBIN" "$DUMPDIR" "$JSONDIR" && \
echo "OK"
