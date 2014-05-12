#!/bin/bash
set -v
#### MVA ####
#screen -m -d -S submit -t "CONTROL" bash -c "while sleep 1h ; do bjobs ; done" ; 

#VAR=pToMscaled
#LABEL=v8
[ -f globaloptions.sh ] && source globaloptions.sh
[ -f global/globaloptions.sh ] && source global/globaloptions.sh

screen -r submit -p 0 -X exec echo "SCREEN is running and attachable"
retval=$?
[ $retval -eq 0 ] || screen -m -d -S submit -t "CONTROL" -l ; 

screen -r submit -p 0 -X exec kinit -R ${USER}@CERN.CH

for VAR in $VARS; do

screen -r submit -d -X screen -fn -t ${LABEL}_${VAR}_data_8TeV  -l bash -c "cd $PWD ;source ~/.bashrc; eval \`scramv1 runtime -sh\`;  python submit_fitter.py -d ${USER}_${LABEL}_${VAR}_Data  -q 8nh -l sub &>log_1.txt" ;
screen -r submit -d -X screen -fn -t ${LABEL}_${VAR}_sig_8TeV  -l bash -c "cd $PWD ;source ~/.bashrc; eval \`scramv1 runtime -sh\`;  python submit_fitter.py -d ${USER}_${LABEL}_${VAR}_Sig  -q 8nh -l sub &>log_2.txt" ;
screen -r submit -d -X screen -fn -t ${LABEL}_${VAR}_syst_8TeV  -l bash -c "cd $PWD ;source ~/.bashrc; eval \`scramv1 runtime -sh\`;  python submit_fitter.py -d ${USER}_${LABEL}_${VAR}_Syst  -q 8nh -l sub &>log_3.txt" ;

done
screen -r submit -p 0 -X exec echo "other windows are submitting. When done you can close this screen."
set +v
