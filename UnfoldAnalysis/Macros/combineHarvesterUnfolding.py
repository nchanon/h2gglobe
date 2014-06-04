#!/usr/bin/python
import os, array
from glob import glob
from subprocess import call
from optparse import OptionParser

def getVariableBins(var):
	wd=os.environ['PWD']
	wd_list=wd.split('/')
	#todo: make it work for any directory that just contains h2gglobe
	h2gglobe=wd_list.index('h2gglobe')
	baseDir="/".join(wd_list[0:h2gglobe+1])
	print "Opening file :", baseDir + "/AnalysisScripts/diffanalysis/vars/" + options.var + ".dat"
	fVar = open( baseDir + "/AnalysisScripts/diffanalysis/vars/" + options.var + ".dat")
	VarDef = ""
	VarCategoryBoundaries=""
	for line in fVar:
		parts=line.split('#')[0].split('=')
		if parts[0] == 'VarDef':
			VarDef = parts[1]
		if parts[0] == 'varCatBoundaries':
			VarCategoryBoundaries= parts[1]
	nBins=0
	print "Boundaries ",
	histBins=[]
	for bound in VarCategoryBoundaries.split(','):
		if bound != "":
			print float(bound),
			histBins.append(float(bound))
			nBins +=1
	print " "
	return (nBins,histBins)


##### CONFIGURATION ######
nPoints_=1000
nJobs_=20
nBins_=6
muRange_=[-3,4]
datacard_="cms_hgg_datacard_8TeV_PtScaled"
mass_=125
expected_=True
queue_="8nh"
dryRun_=False
filesToCopy_=["CMS-HGG_mva_8TeV_multipdf.root","CMS-HGG_mva_8TeV_sigfit.root"]
hadd_=False
dir_="jobs"
StatOnly_=False
ProfileMH_=False
SkipWs_=False
ResubmitFail_=False
ResubmitRun_=False
Var_=""
##########################

############PARSER ##################
if __name__=="__main__":
	usage = "usage: %prog [options]"
	parser=OptionParser(usage=usage)
	parser.add_option("-d","--datacard" ,dest='datacard',type='string',help="datacard. Default=%default",default=datacard_)
	parser.add_option("-v","--var" ,dest='var',type='string',help="variables name. Default=%default",default=Var_)
	parser.add_option("-u","--unblind" ,dest='unblind',action='store_true',help="Unblind. Default=%default",default=False)
	parser.add_option("-r","--murange" ,dest='murange',type='string',help="MuRange. Default=%default",default="%f,%f"%(muRange_[0],muRange_[1]))
	parser.add_option("-D","--dir" ,dest='dir',type='string',help="Script Directory & results. Default=%default",default=dir_)
	parser.add_option("-q","--queue" ,dest='queue',type='string',help="Batch Queue. Default=%default",default=queue_)
	parser.add_option("-m","--mass",dest='mass',type='float',help="Mass Point. Default=%default",default=mass_)
	parser.add_option("-n","--dryRun",dest='dryRun',action='store_true',help="DryRun. Default=%default",default=dryRun_)
	parser.add_option("-s","--StatOnly",dest='StatOnly',action='store_true',help="StatOnly Default=%default",default=StatOnly_)
	parser.add_option("","--ProfileMH",dest='ProfileMH',action='store_true',help="ProfileMH Default=%default",default=ProfileMH_)
	parser.add_option("","--skipWs",dest='SkipWs',action='store_true',help="Skip Ws. Default=%default",default=SkipWs_)
	parser.add_option("","--nJobs",dest='nJobs',type='int',help="nJobs per Bin in submission. Default=%default",default=nJobs_)
	parser.add_option("","--nBins",dest='nBins',type='int',help="nBins . Default=%default",default=nBins_)
	parser.add_option("","--nPoints",dest='nPoints',type='int',help="nPoints per Bin in submission. Default=%default",default=nPoints_)
	parser.add_option("","--hadd",dest='hadd',action='store_true',help="DoHadd instead. Default=%default",default=hadd_)
	parser.add_option("","--resubmitFail",dest='resubmitFail',action='store_true',help="Resubmit Failed jobs. Default=%default",default=ResubmitFail_)
	parser.add_option("","--resubmitRun",dest='resubmitRun',action='store_true',help="Resubmit Runed jobs. Default=%default",default=ResubmitRun_)
	(options,args)=parser.parse_args()
	
	dryRun_=options.dryRun
	mass_=options.mass
	datacard_=options.datacard
	if ( datacard_.rfind(".txt") >=0 ) :
		datacard_= datacard_[0:datacard_.rfind(".txt")]
	queue_=options.queue
	nJobs_=options.nJobs
	nBins_=options.nBins
	nPoints_=options.nPoints
	hadd_=options.hadd
	dir_=options.dir
	if options.unblind: expected_=False
	StatOnly_=options.StatOnly
	ProfileMH_=options.ProfileMH
	SkipWs_=options.SkipWs
	ResubmitFail_=options.resubmitFail
	ResubmitRun_=options.resubmitRun
	if ResubmitFail_ or ResubmitRun_:
		if not SkipWs_: print "Setting Skip Ws Option!"
		SkipWs_=True
	muRange_[0]=float(options.murange.split(",")[0])
	muRange_[1]=float(options.murange.split(",")[1])
	Var_=options.var
	if Var_ != "":
		nBinsOld=nBins_
		nBins_=getVariableBins(Var_)[0] + 1
		print "Changing binning from",nBinsOld,
		print "to",nBins_,"because variable settings are declared"

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

	if iBin==0 and iJob==0:
		cmd="cp -v %s/%s.root %s/%s/ "%(os.environ['PWD'],datacard_,os.environ['PWD'],dir_)
		call(cmd.split()) 
		cmd="cp -v %s/%s.txt %s/%s/"%(os.environ['PWD'],datacard_,os.environ['PWD'],dir_)
		call(cmd.split()) 

	out += "cp %s/%s/%s.root ./\n"%(os.environ['PWD'],dir_,datacard_)
	out += "cp %s/%s/%s.txt ./\n"%(os.environ['PWD'],dir_,datacard_)
	for f in filesToCopy_:
		out += "cp %s/%s/%s ./ \n"%(os.environ['PWD'],dir_,f)
		if iBin==0 and iJob==0:
			cmd="cp -v %s/%s %s/%s/%s"%(os.environ['PWD'],f,os.environ['PWD'],dir_,f)
			print "cmd is"
			print "    ",cmd
			call(cmd.split(' ')) 

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
	if ProfileMH_:
		out+=" -P MH"
	#extra options
	#out += '--protectUnbinnedChannels '
	out += '--saveNLL '

	out += "\n\n"
	out += "RESULT=$?\n"
	out += "mv -v higgsCombine* %s/%s/ \n"%(os.environ['PWD'],dir_)
	out += "\n"
	out += "rm %s \n"%(runFile)
	out += '[ "$RESULT" == "0" ] && { echo DONE; touch %s; } || echo $RESULT > %s'%(doneFile,failFile)
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
	if SkipWs_ :print cmd;
	else: call(cmd.split())

def GetListOfJobs(l):
	R=[]
	for fileName in l:
		if fileName.rfind("/") >=0:
			baseName=fileName[ fileName.rfind("/")+1:]
		else:
			basename=fileName
		#jobInfo_Bin3_Job4.fail
		if baseName.rfind('.') <0 :
			print "Error in fileName",fileName,"should have an extension .fail,.run,.done"
		baseName=baseName[0:baseName.rfind('.')]
		#jobInfo_Bin3_Job4
		parts=baseName.split("_")
		sBin=parts[1]
		sJob=parts[2]
		iBin=int(sBin.replace("Bin",""))
		iJob=int(sJob.replace("Job",""))

		R.append( (iBin,iJob) )
	return R


def ResubmitFail(type=0):
	l_fail = GetListOfJobs( glob("%s/*fail"%(dir_)) )
	l_done  = GetListOfJobs( glob("%s/*done"%(dir_)) )
	l_run = GetListOfJobs( glob("%s/*run"%(dir_))  )
	tot=len(l_fail)+len(l_run)+len(l_done)

	Red="\x1b[01;31m"
	Green="\x1b[01;32m"
	Yellow="\x1b[01;33m"
	EndColor="\x1b[00m"

	print "Jobs %srunning%s (%d/%d):"%(Yellow,EndColor,len(l_run),tot)
	for (iBin,iJob) in l_run: 
		print "Bin%d_Job%d "%(iBin,iJob),
	print "\nJobs %sdone%s (%d/%d):"%(Green,EndColor,len(l_done),tot)
	for (iBin,iJob) in l_done:
		print "Bin%d_Job%d "%(iBin,iJob),
	print "\nJobs %sfail%s (%d/%d):"%(Red,EndColor,len(l_fail),tot)
	for (iBin,iJob) in l_fail:
		print "Bin%d_Job%d "%(iBin,iJob),

	if type==0: l_resub=l_fail
	elif type==1: l_resub=l_run
	elif type==2: 
		l_resub=l_fail	
		l_resub += l_run

	print "\nGoing To Resubmit\n"
	for (iBin,iJob) in l_resub:
		doneFile="%s/%s/jobInfo_Bin%d_Job%d.done"%(os.environ['PWD'],dir_,iBin,iJob ) 
		failFile="%s/%s/jobInfo_Bin%d_Job%d.fail"%(os.environ['PWD'],dir_,iBin,iJob ) 
		runFile ="%s/%s/jobInfo_Bin%d_Job%d.run" %(os.environ['PWD'],dir_,iBin,iJob ) 
		logFile ="%s/%s/jobInfo_Bin%d_Job%d.log" %(os.environ['PWD'],dir_,iBin,iJob ) 
		scriptFile = "%s/%s/job_Bin%d_Job%d.sh"  %(os.environ['PWD'],dir_,iBin,iJob )
		cmd = "bsub -q %s -J Combine_Bin%d_Job%d -o %s %s"%(queue_,iBin,iJob,logFile,scriptFile)
		if dryRun_: print cmd
		else: call(cmd.split())

if __name__=="__main__":
    ##figure out files from datacard	
    filesToCopy_.extend( getFilesFromDatacard(datacard_+".txt").split(',') )
    if hadd_:
	print "## Hadd"
	for iBin in range(0,nBins_):
		fileList=glob("%s/higgsCombineJob_*_Bin_%d.MultiDimFit.*.root"%(dir_,iBin))
		cmdList=["hadd","%s/MultiDimFit_Bin%d.root"%(dir_,iBin)]
		cmdList+=fileList	
		if dryRun_: print ' '.join(cmdList);
		else: call(cmdList);
    elif ResubmitFail_ :
	ResubmitFail()
    elif ResubmitRun_:
	ResubmitFail(1)
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


