DUMPDIR=bin/dump
JSONDIR=bin/jsondump
TOJSONBIN=$(pwd)/../../tools/crtojson.sh
GENERATOR=$(pwd)/../generator/criugen.py

echo Killing processes... && \
./get_all_pids.py bin/cmds.json | xargs -n 1 sudo kill -9

make clean all && \
sudo rm -f interpreter_log.log
sudo bin/restorer bin/cmds.json &
sudo cat interpreter_log.log
ROOT_PID=$(./get_root_pid.py bin/cmds.json)
echo ROOT_PID = $ROOT_PID
sudo cat interpreter_log.log
mkdir -p $DUMPDIR && \
mkdir -p $JSONDIR && \
echo "DUMPING VIA CRIU..." && \
sudo criu dump -t "$ROOT_PID" -D "$DUMPDIR" -vvv -o dump.log && \
echo OK, Converting to json... && \
"$TOJSONBIN" "$DUMPDIR" "$JSONDIR" && \
echo OK && \
"$GENERATOR" "$DUMPDIR"
