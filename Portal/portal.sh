#!/bin/bash

option=$1
function start {
	prev=$(pwd)
	cd /home/pi/MonitoringBox/Portal
#	if [ ! -f /var/run/monitoringboxpid ]; then

		python3 ./main.py  > /dev/null 2>&1 &
		FOO_PID=$!
		echo $FOO_PID > /var/run/monitoringboxpid
#	fi
	cd $prev
}

function stop {
	pid=$(cat /var/run/monitoringboxpid)
	kill $pid
}

function status {
	if [ -f /var/run/monitoringboxpid ]; then
		echo "Monitoringbox is running"
	else
		echo "Monitoringbox is not running"
	fi
}
case "$option" in
	start)
		start
		;;
	stop)
		stop
		;;
	status)
		status
		;;
	restart)
		stop
		start
		;;
	*)
		echo $"Usage: $0 {start|stop|restart|condrestart|status}"
		exit 1
esac


