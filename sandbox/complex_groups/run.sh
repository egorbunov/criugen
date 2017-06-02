#! /bin/bash
BINDIR=$(pwd)/bin
BIN=$BINDIR/complex_groups
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

echo "Building..." && \
make all LOG_IMPORTANT=1 && \

echo "Running detached [$BIN \"${LOGFILE}\"] detached..."
$BIN "${LOGFILE}" &

echo "Waiting for process to start and print it's PID..."
slept=0
while [ "$(cat "$LOGFILE" | wc -l)" -le 1 ]; do 
	sleep 0.1
	slept=$((slept+1))
	if [ $slept -eq 100 ]; then
		echo "Waiting too long!"
		break
	fi
done

PID=$(cat "$LOGFILE" | head -n 1)
echo "Target process tree root PID = [$PID]"

echo "Waiting for process tree state to prepare for dumping..."
slept=0
while [ "$(cat "$LOGFILE" | tail -n 1 | tr -d '\n ')" != "FINISH" ]; do 
	sleep 0.1
	slept=$((slept+1))
	if [ $slept -eq 100 ]; then
		echo "Waiting too long!"
		break
	fi
done

echo "Dumping...${PID}" && \
sudo criu dump -t "$PID" -D "$DUMPDIR" -vvv -o dump.log && \
echo "OK" && \
echo "Converting to json..." && \
"$TOJSONBIN" "$DUMPDIR" "$JSONDIR" && \
echo "==== LOG ====" && \
cat "$LOGFILE" | ccze -A && \
echo "OK"
