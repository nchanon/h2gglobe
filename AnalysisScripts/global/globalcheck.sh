#!/bin/bash
set -v

#VAR=pToMscaled
#LABEL=v8
[ -f globaloptions.sh ] && source globaloptions.sh
[ -f global/globaloptions.sh ] && source global/globaloptions.sh

screen -r check -p 0 -X exec echo "SCREEN is running and attachable"
retval=$?
[ $retval -eq 0 ] || screen -m -d -S check -t "CONTROL" -l 
screen -r check -p 0 -X exec kinit -R ${USER}@CERN.CH

screen -r check -d -X screen -fn -t ticket_renewal  bash -c "cd $PWD ;source ~/.bashrc; eval \`scramv1 runtime -sh\`; while sleep 6h ; do  echo renewing now ... ; date ; kinit -R ; done" 

for VAR in $VARS ; do

 screen -r check -d -X screen -fn -t ${LABEL}_${VAR}_Sig_8TeV  bash -c "cd $PWD ;source ~/.bashrc; eval \`scramv1 runtime -sh\`;while( ! ./check_fitter.py ${USER}_${LABEL}_${VAR}_Sig  ); do sleep 360 ; done" 
 screen -r check -d -X screen -fn -t ${LABEL}_${VAR}_Data_8TeV  bash -c "cd $PWD ;source ~/.bashrc; eval \`scramv1 runtime -sh\`;while( ! ./check_fitter.py ${USER}_${LABEL}_${VAR}_Data  ); do sleep 360 ; done" 
 screen -r check -d -X screen -fn -t ${LABEL}_${VAR}_Syst_8TeV  bash -c "cd $PWD ;source ~/.bashrc; eval \`scramv1 runtime -sh\`;while( ! ./check_fitter.py ${USER}_${LABEL}_${VAR}_Syst  ); do sleep 360 ; done" 

 done

 screen -r check -p 0 -X exec echo "other windows are checking and right after merging. When done close this screen. "
 echo "$(hostname) $LABEL $VARS" >> ~/check_host.txt
set +v
