PROGRAM_FILE=$1
LOG_FILE=restore.log

sudo rm -f $LOG_FILE && \
touch $LOG_FILE && \
sudo bin/restorer -l $LOG_FILE $PROGRAM_FILE && \
sleep 2 && \
cat $LOG_FILE | ccze -A
