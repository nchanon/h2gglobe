#Instructions for differential Analysis

###Installation
* create a CMSSW\_6\_1\_X release
* clone the repository and checkout the correct tag (the branch is *topic_diffAnalysisAndUnfolding* )

        git clone git@github.com:amarini/h2gglobe  
        cd h2gglobe
        git checkout diffanalysis_ws_v1
* compile the repository [slc5]  

        make -j 16
* compile the subpackages [slc5]  

        cd SimultaneousSignalFitting/
        make -j 16
        cd -
        cd BackgroundProfileFitting/
        make -j 16
        cd -

###Job creation and submission
* go in the script directory  

        cd AnalysisScripts
* edit global/globaloptions.sh  
  variables name should match the one in diffanalysis/vars/*.dat

        VARS="pToMscaled"
        LABEL="diffanalysis_v1"

* create the jobs [this script calls mk_fitter, you can use it directly if you prefer]

        ./global/globalcreate.sh
* submit jobs to the batch  [slc6]  
   the "*global*" script spawn a screen (submit) that does the submission of all the directories and all the jobs.

        ./global/globalsubmit.sh
        or (especially if somthing fails) ./submit_fitter.py -q 8nh -d dir [ -j 1,2,5... ]

* check jobs  
   the check_fitter.py (run in loop) will check the jobs status, resubmit some of them according to the failure, and merge them when done.
   I saw that eos is starting to raise errors that it does not resubmit (and maybe we don't want to do automatically in case of I/O readwrite -> missing file) so in case try to resubmit it once or twice.

        ./global/globalcheck.sh  
        screen -r check
        kinit [enter your pwd]

###Signal Fit
> ``the fun is yet to come''  

Signal fit is painful, because we must check that fits converges everywhere.
* go in the signal fitting directory:
* The Categories are the nBins*nCatsPerBin, while the last Bin is nBins (ie, from 0<= to <=nBins)  

~~~
cd SimultaneousSignalFitting
./bin/calcPhotonSystConsts -i ../CMS-HGG_syst.root -m 125 -n 20 -p `echo Bin{0..5} | tr ' ' ','` -o dat/unfoldPhotonCatSyst.dat
./bin/SignalFit -i ../CMS-HGG_sig.root -d dat/unfoldAnalysis.dat -s dat/unfoldPhotonCatSyst.dat -L 120 -H 130 --nCats 20 --procs `echo Bin{0..5} | tr ' ' ',' `
~~~

* **unfoldPhotonCatSyst.dat**: before fitting, check if there are some inf or nan inside. (Very likely they come from null histograms so they can be set to 0)       
* **unfoldAnalysis.dat**: this guy must be optimized ! 
       * start w/ something reasonable (diagonal 4 3) off-diagonal-by-one (2 2) and others from the diagonal bin

~~~
python h2gglobe/UnfoldAnalysis/Macros/makeDiagonalDat.py --help
~~~
* 
       * try to fit 
       * check the plots, are they ok ? 
       * check the ws. (if there are no complains its fine, pdfs are >0, otherwise combine will not be able to produce sensible results)

~~~
python checkSignalWs.py -s filename -n bins -c cats -S 0.5 
~~~


###Background envelope
Background Fit will create the ws with the envelope
* go in the background profile fitting directory:  
  the number of categories refers to the nBins*nCatsPerBin

       ./bin/fTest -i ../CMS-HGG_data.root -c nCat --saveMultiPdf ../CMS-HGG_multipdf.root
* save somewhere (or set them in the fTest command) the plots produced directory *plots*, and the dat file produced *dat/fTest.dat* because these will be used later for check and bias studies.
* The bias studies are run w/ the program

~~~
./bin/Bias
~~~
* Trough the scripts in 

~~~
python scripts/sub_coverage_jobs.py 
-s CMS-HGG_Sig.root # not signafit
-b CMS-HGG_Data.root
-t 50 # n. of toys
-c 0 # one for each category 0,1,2 ...
--nBins 7 
-d dat/fTest.dat # the one produced by the multipdf fits
-e /store/user/amarini/HGG/Bias
-j 0 
-n 100 # nJobs
-o jobs #outputdir
-L 0 -H 2 -S .1 # range and step of mu 
python scripts/make_hists_from_raw_files.py --eosWalk=100 --expectSignal=1  -D /store/user/amarini/HGG/Bias/jobs/cat0_mu1.0/ --runSpecificFiles='0' -o jobs/cat0_mu1.0.root
~~~


###Miscellaneous
* **screen**: a very useful tool. It spawn shell(s) that are kept alive running on the background of the machine, and you can re-attach them.
   usage on lxplus, is simple:
   this will gave the screen a ticket that grants it the same privilege you have also when you detach it.

         screen -m
         kinit [enter your pwd]
         C-A c
         C-A "
         C-A d
         screen -r
      
* **mk_fitter.py**:

         ./mk_fitter.py -i datfile -n njobs -v varname [--onlyData/onlySig] -o outdir
* **slc5** / **slc6**:
   compilation works on slc5
   submission to batch (due to queue limits) should be done only on slc6
   after doing cmsenv, some libraries stops to work on slc6, you can restore (some of them w/):

        SLC=$(lsb_release -r | tr '\t' ' '| tr -s ' ' | cut -d ' ' -f2)
        SLC6=$( echo "$SLC > 5.9" | bc -lq )
        alias slc6='[ ${SLC6} -eq 1 ] && LD_LIBRARY_PATH=/lib64:/usr/lib64/perl5/CORE:$LD_LIBRARY_PATH'
        #
        slc6
* the "*global*" scripts spawn two screens (check & submit):

        $screen -ls
        There are screens on:
          28592.submit    (Detached)
          30920.check    (Detached)

if you forgot where, the globalcheck appends a line in  

         $cat ~/check_host.txt
         lxplus0057.cern.ch diffanalysis_v1 pToMscaled dPhi
so you can go bach there and re-attach it in case you forgot where it was.

* **mail**: you can use them to tell you when something is done (in a screen for example). No jobs in batch-queues, like:

~~~
UnfoldAnalysis/Macros/checkCmdMail.sh:
while sleep 10m ; do 
   if (  bjobs   | grep -v JOBID | wc -l | grep '^0$'  ) ; then
      echo "DONE" | mail -s BATCH_Done -r amarini@cern.ch amarini@cern.ch ;
      break;
   fi;
done
~~~
