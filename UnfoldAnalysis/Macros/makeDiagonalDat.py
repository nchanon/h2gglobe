#!/bin/env python
import os,sys
from optparse import OptionParser

if __name__=="__main__":
	usage = "usage: %prog [options]"
	parser=OptionParser(usage=usage)
	parser.add_option("-f","--file" ,dest='file',type='string',help="dat output file. Default=%default",default="output.dat")
	parser.add_option("-n","--nBins" ,dest='nBins',type='int',help="Number Of Bins. Default=%default",default=5 )
	parser.add_option("-c","--nCats" ,dest='nCats',type='int',help="Number Of Cats. Default=%default",default=20)
	(options,args)=parser.parse_args()



if __name__=="__main__":
	
	f=open(options.file,"w")
	nBins=options.nBins
	nCats=options.nCats

	f.write("# proc cat nGausRV nGausWV\n")

	for iBin in range(0,nBins+1):
	   diagonal=""
	   offdiagonal=""
	   for iCat in range(0,nCats):
		   if iCat % ( nBins ) == iBin or iBin==nBins+1:
			   diagonal += "Bin%d %d 4 3\n"%(iBin,iCat)
		   else:
			   if iCat % (nBins) == iBin + 1: # super diaganol
			   	offdiagonal += "Bin%d %d 2 2\n"%(iBin,iCat)
			   else:
			   	offdiagonal += "Bin%d %d 4 3 Bin%d %d\n"%(iBin,iCat,iBin,iCat % (nBins)+iBin)

	   f.write("### BIN %d ###\n"%iBin)
	   f.write(diagonal)
	   f.write("# -> off-diagonal\n")
	   f.write(offdiagonal)
	


