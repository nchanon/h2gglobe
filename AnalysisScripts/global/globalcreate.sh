#!/bin/bash
set +v

#LABEL=v8
#VAR=pToMscaled
[ -f globaloptions.sh ] && source globaloptions.sh
[ -f global/globaloptions.sh ] && source global/globaloptions.sh

echo "Checking and creating pevents"
#Create Pevents -- allow mkfitter to do them concurrently is not a good idea

function create_pevents(){
	dat=$1
	tmpdat=${dat/datafile/tmp_datafile}
	echo "Dat file $dat tmp $tmpdat"
	[ -e $tmpdat.pevents ] || python mk_pevents_fast.py $dat
	#[ -e $tmpdat.pevents ] || { cp $dat $tmpdat ; python fitter.py  -i $tmpdat --dryRun &> $tmpdat.log ; }
	echo "Done $tmpdat"
	}

#create_pevents "massfac_mva_binned/datafiles_massfacmva_legacy.dat"  & 

#create_pevents "diffanalysis/datafiles_differentialanalysis.dat" &
#create_pevents "diffanalysis/datafiles_differentialanalysis_systs.dat" &
create_pevents "diffanalysis/datafiles_differentialanalysis_massfacmva_systs.dat" &
create_pevents "diffanalysis/datafiles_differentialanalysis_massfacmva.dat" &

wait

#### MVA ####
for VAR in $VARS ; do

./mk_fitter.py -i diffanalysis/datafiles_differentialanalysis_massfacmva.dat -n 50 -v ${VAR} --onlySig  -l ${LABEL} -o ${USER}_${LABEL}_${VAR}_Sig  &
./mk_fitter.py -i diffanalysis/datafiles_differentialanalysis_massfacmva_systs.dat -n 10 -v ${VAR} --onlySig  -l Syst_${LABEL} -o ${USER}_${LABEL}_${VAR}_Syst  &
./mk_fitter.py -i diffanalysis/datafiles_differentialanalysis_massfacmva.dat -n 50 -v ${VAR} --onlyData -l ${LABEL} -o ${USER}_${LABEL}_${VAR}_Data  &
## BKG ##
#./mk_fitter.py -i massfac_mva_binned/datafiles_massfacmva_legacy.dat -n 50  --onlyBkg -l legacy_paper_8TeV_${LABEL} -o ${USER}_mva_8TeV_Bkg  &

done 

echo "Waiting"
wait
echo "DONE"
set -v
