#!/usr/bin/python
import os, array
from glob import glob
from subprocess import call
from optparse import OptionParser


##### CONFIGURATION ######
nPoints_=1000
nJobs_=20
nBins_=6
muRange_=[0,4]
datacard_="cms_hgg_datacard_8TeV_PtScaled"
mass_=125
expected_=True
queue_="8nh"
dryRun_=False
filesToCopy_=["CMS-HGG.root","CMS-HGG_sigfit.root"]
hadd_=False
dir_="jobs"
StatOnly_=False
ProfileMH_=False
##########################

############PARSER ##################
if __name__=="__main__":
	usage = "usage: %prog [options]"
	parser=OptionParser(usage=usage)
	parser.add_option("-d","--datacard" ,dest='datacard',type='string',help="datacard (w/o txt extension). Default=%default",default=datacard_)
	parser.add_option("-u","--unblind" ,dest='unblind',action='store_true',help="Unblind. Default=%default",default=False)
	parser.add_option("-D","--dir" ,dest='dir',type='string',help="Script Directory & results. Default=%default",default=dir_)
	parser.add_option("-q","--queue" ,dest='queue',type='string',help="Batch Queue. Default=%default",default=queue_)
	parser.add_option("-m","--mass",dest='mass',type='float',help="Mass Point. Default=%default",default=mass_)
	parser.add_option("-n","--dryRun",dest='dryRun',action='store_true',help="DryRun. Default=%default",default=dryRun_)
	parser.add_option("-s","--StatOnly",dest='StatOnly',action='store_true',help="StatOnly Default=%default",default=StatOnly_)
	parser.add_option("","--ProfileMH",dest='ProfileMH',action='store_true',help="ProfileMH Default=%default",default=ProfileMH_)
	parser.add_option("","--nJobs",dest='nJobs',type='int',help="nJobs per Bin in submission. Default=%default",default=nJobs_)
	parser.add_option("","--nBins",dest='nBins',type='int',help="nBins . Default=%default",default=nBins_)
	parser.add_option("","--nPoints",dest='nPoints',type='int',help="nPoints per Bin in submission. Default=%default",default=nPoints_)
	parser.add_option("","--hadd",dest='hadd',action='store_true',help="DoHadd instead. Default=%default",default=hadd_)
	(options,args)=parser.parse_args()
	
	dryRun_=options.dryRun
	mass_=options.mass
	datacard_=options.datacard
	queue_=options.queue
	nJobs_=options.nJobs
	nBins_=options.nBins
	nPoints_=options.nPoints
	hadd_=options.hadd
	dir_=options.dir
	if options.unblind: expected_=False
	StatOnly_=options.StatOnly
	ProfileMH_=options.ProfileMH
#####################################

def getFilesFromDatacard(datacard):
    card = open(datacard,"r")
    files = set()
    for l in card.read().split("\n"):
        if l.startswith("shape"):
            toks = [t for t in l.split(" ") if t != "" ]
            files.add(toks[3])
    files = list(files)
    ret = files[0]
    for f in files[1:]:
        ret += ",%s" % f
    return ret

def WriteExe(iBin,iJob):
	''' Write Executable to run on batch and submit. It uses global variables '''
	out  = "#!/bin/bash \n"
	out += "cd %s \n"%(os.environ['PWD'])
	call(["mkdir","-p",dir_])
	doneFile="%s/%s/jobInfo_Bin%d_Job%d.done"%(os.environ['PWD'],dir_,iBin,iJob ) 
	failFile="%s/%s/jobInfo_Bin%d_Job%d.fail"%(os.environ['PWD'],dir_,iBin,iJob ) 
	runFile ="%s/%s/jobInfo_Bin%d_Job%d.run" %(os.environ['PWD'],dir_,iBin,iJob ) 
	logFile ="%s/%s/jobInfo_Bin%d_Job%d.log" %(os.environ['PWD'],dir_,iBin,iJob ) 
	scriptFile = "%s/%s/job_Bin%d_Job%d.sh"  %(os.environ['PWD'],dir_,iBin,iJob )
	out += "rm %s \n"%(doneFile)
	out += "rm %s \n"%(failFile)
	out += "touch %s \n"%(runFile)
	out += "eval `scramv1 runtime -sh`\n"
	## move to WorkDir and copy files
	out += "cd $WORKDIR\n"
	out += "cp %s/%s.root ./\n"%(os.environ['PWD'],datacard_)
	out += "cp %s/%s.txt ./\n"%(os.environ['PWD'],datacard_)
	for f in filesToCopy_:
		out += "cp %s/%s ./ \n"%(os.environ['PWD'],f)

	## construct combine line
	out += "combine "
	if StatOnly_: out += " -S0 "
	# expected
	if expected_: out += "-t -1 --expectSignal=1 --expectSignalMass=%f "%(mass_)
	# method
	out += '%s.root -M MultiDimFit --X-rtd ADDNLL_FASTEXIT --keepFailures --cminDefaultMinimizerType Minuit2 '%(datacard_) 
	#algorithm + grid options
	out += '--algo=grid --points=%d --firstPoint=%d --lastPoint=%d -n Job_%d_Bin_%d '%(nPoints_,int(nPoints_/nJobs_ *iJob), int(nPoints_/nJobs_*(iJob+1)),iJob,iBin)
	# method options
	out += '-m %f -P "r_Bin%d" --floatOtherPOIs=1 --squareDistPoiStep ' %(mass_,iBin)
	if ProfileMH:
		out+=" -P MH"
	#extra options
	#out += '--protectUnbinnedChannels '
	out += '--saveNLL '

	out += "\n\n"
	out += "RESULT=$?\n"
	out += "mv -v higgsCombine* %s/%s/ \n"%(os.environ['PWD'],dir_)
	out += "\n"
	out += "rm %s \n"%(runFile)
	out += '[ "$RESULT" == "0" ] && { echo DONE; touch %s; } || touch  %s'%(doneFile,failFile)
	outFile=open(scriptFile,"w")
	outFile.write(out)
	outFile.close()

	cmd = "chmod u+x %s"%(scriptFile)
	if dryRun_: print cmd
	else: call(cmd.split())

	cmd = "bsub -q %s -J Combine_Bin%d_Job%d -o %s %s"%(queue_,iBin,iJob,logFile,scriptFile)
	if dryRun_: print cmd
	else: call(cmd.split())


def CreateWS():
	cmd ="text2workspace.py %s.txt -o %s.root -m %f -P h2gglobe.AnalysisScripts.UnfoldModel:unfoldModel --PO nBin=%d --PO range=%f:%f" %(datacard_,datacard_,mass_,nBins_,muRange_[0],muRange_[1])
	if dryRun_:print cmd;
	else: call(cmd.split())

if __name__=="__main__":
    if hadd_:
	print "## Hadd"
	for iBin in range(0,nBins_):
		fileList=glob("%s/higgsCombineJob_*_Bin_%d.MultiDimFit.*.root"%(dir_,iBin))
		cmdList=["hadd","%s/MultiDimFit_Bin%d.root"%(dir_,iBin)]
		cmdList+=fileList	
		if dryRun_: print ' '.join(cmdList);
		else: call(cmdList);
    else:
	print "## Creating WorkSpace"
	CreateWS()
	print "## Submitting Jobs"
	if nPoints_%nJobs_!=0: 
		print "## ERROR nPoist%nJobs !=0: ",
		nPoints_=int(nPoints_/nJobs_) * nJobs_
		print "## new nPoints is ",nPoints_
	for iJob in range(0,nJobs_):
	   for iBin in range(0,nBins_):
		WriteExe(iBin,iJob)


