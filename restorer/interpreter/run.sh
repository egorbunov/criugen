make clean all && \
sudo rm -f interpreter_log.log && \
sudo bin/restorer bin/cmds.json && \
sleep 1 && \
sudo cat interpreter_log.log
