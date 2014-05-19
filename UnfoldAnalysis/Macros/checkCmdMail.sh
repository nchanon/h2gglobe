while sleep 10m ; 
do 
if (  bjobs   | grep -v JOBID | wc -l | grep '^0$'  ) ; 
	then 
		echo "DONE" | mail -s BATCH_Done -r amarini@cern.ch amarini@cern.ch ;  
		break ; 
	fi ; 
done 
