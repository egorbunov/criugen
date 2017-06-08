PROGRAM_FILE=$1
FIN_PROG=build/fin_prog.json
LOG_FILE=build/restore.log
DUMPDIR=build/dump
JSONDIR=build/jsondump
TOJSONBIN=$(pwd)/../../tools/crtojson.sh
GENERATOR=$(pwd)/../generator/criugen.py

echo Killing processes... && \
./get_all_pids.py $PROGRAM_FILE | xargs -n 1 sudo kill -9

sudo rm -f $LOG_FILE && \
touch $LOG_FILE && \
sudo build/restorer -l $LOG_FILE $PROGRAM_FILE && \
sleep 2 && \
cat $LOG_FILE | ccze -A
ROOT_PID=$(./get_root_pid.py $PROGRAM_FILE)
echo ROOT_PID = $ROOT_PID
sudo cat interpreter_log.log
mkdir -p $DUMPDIR && \
mkdir -p $JSONDIR && \
echo "DUMPING VIA CRIU..." && \
sudo criu dump -t "$ROOT_PID" -D "$DUMPDIR" -vvv -o dump.log && \
echo OK, Converting to json... && \
"$TOJSONBIN" "$DUMPDIR" "$JSONDIR" && \
echo OK && \
"$GENERATOR" "$DUMPDIR" "$FIN_PROG" && \
diff $PROGRAM_FILE $FIN_PROG && echo "EQUAL ==> OK!"
