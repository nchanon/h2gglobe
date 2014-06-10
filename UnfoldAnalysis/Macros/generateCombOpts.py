#!env python

import os, array, sys
from glob import glob
from subprocess import call
from optparse import OptionParser

## configure options
if __name__=='__main__':
	usage = "usage: %prog [options]"
	parser=OptionParser(usage=usage)
	parser.add_option("-v","--var" ,dest='var',type='string',help="variables name. Default=%default",default="pToMscaled")
	(options,args)=parser.parse_args()
	sys.argv=[]

def WritePreamble(file,var):
	''' Write file and datacard configuration '''
	file.write("#card and file opts\n");
	file.write("datacard=cms_hgg_datacard_%s.txt\n"%var);
	file.write("\n")

def WriteLine(file,var,iBin,method='',extraString=''):
		dict={'extra':extraString,'bin':iBin,'var':var,'method':method}
		if method == 'RBinScan':
			dict['outdir']='%(var)s/RecoScan%(extra)sExpBin%(bin)d'%dict
		elif method== 'RDiffXsScan':
			dict['outdir']='%(var)s/UnfoldScan%(extra)sExpBin%(bin)d'%dict
		else:
			dict['outdir']='outdir'
		dict['mh']=125.
		dict['muLow']=-1.
		dict['muHigh']=3.
		dict['jobs']=5
		dict['pointsperjob']=10
		if iBin==0:
			dict['skipWs']=''
		else:
			dict['skipWs']='skipWorkspace'
		dict['opts']='opts=--squareDistPoi'
		dict['poix']='r_Bin%(bin)d'%dict
		dict['exp']='expected=1 expectSignal=1 expectSignalMass=%(mh)f'%dict
		if extraString=='Stat':
			dict['stat']='freezeAll=1'
		else:
			dict['stat']=''

		file.write("outDir=%(outdir)s/ method=%(method)s mh=%(mh)f muLow=%(muLow)f muHigh=%(muHigh)f jobs=%(jobs)d  pointsperjob=%(pointsperjob)d var=%(var)s poix=%(poix)s %(exp)s %(opts)s %(skipWs)s %(stat)s\n"%dict)

def findPath():
	#figure out globe name
	globe_name = "h2gglobe"
	mypath = os.path.abspath(os.getcwd())
	while mypath != "":
	    if "h2gglobe" in os.path.basename(mypath):
	        globe_name = os.path.basename(mypath)
	        break
	    mypath = os.path.dirname(mypath)
	return (mypath,globe_name)


##Add combineHarverste.py in path
(mypath,globe_name)=findPath()  
sys.path.append(mypath+"/Macros/FinalResults")  

from combineHarvester import getVariableBins

if __name__=="__main__":

	nBins_=getVariableBins(options.var)[0] 

	file=open("combOpts_%s.dat"%options.var,"w")

	WritePreamble(file,options.var)
	file.write('\n\n### RECO SCAN ###\n')
	for iBin in range(0,nBins_):
		WriteLine(file,options.var,iBin,'RBinScan','')
	file.write('\n\n### UNFOLD SCAN ###\n')
	for iBin in range(0,nBins_):
		WriteLine(file,options.var,iBin,'RDiffXsScan','')
	file.write('\n\n### STAT ONLY ###\n')
	for iBin in range(0,nBins_):
		WriteLine(file,options.var,iBin,'RBinScan','Stat')
	file.write('\n\n')
	for iBin in range(0,nBins_):
		WriteLine(file,options.var,iBin,'RDiffXsScan','Stat')
	file.write('\n\n')
	file.close()
