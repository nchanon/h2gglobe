#!/bin/env python
import os,sys
from optparse import OptionParser

if __name__=="__main__":
	usage = "usage: %prog [options]"
	parser=OptionParser(usage=usage)
	parser.add_option("-s","--signal" ,dest='file',type='string',help="sigfit file. Default=%default",default="CMS-HGG_sigfit.root")
	parser.add_option("-n","--nBins" ,dest='nBins',type='int',help="Number Of Bins. Default=%default",default=5 )
	parser.add_option("-c","--nCats" ,dest='nCats',type='int',help="Number Of Cats. Default=%default",default=20)
	parser.add_option("-w","--workspace" ,dest='ws',type='string',help="ws name. Default=%default",default="wsig_8TeV")
	parser.add_option("-m","--mass" ,dest='m',type='float',help="mass (MH). Default=%default",default=125.)
	parser.add_option("-L","--Low" ,dest='low',type='float',help="low mass (cms_hgg). Default=%default",default=110.)
	parser.add_option("-H","--High" ,dest='high',type='float',help="high mass (cms_hgg). Default=%default",default=150.)
	parser.add_option("-S","--Step" ,dest='step',type='float',help="step. Default=%default",default=.1)
	(options,args)=parser.parse_args()


import ROOT
#wsig_8TeV:hggpdfsmrel_8TeV_Bin0_$CHANNEL
#cat0 ...
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so")

if __name__=="__main__":
	
	f=ROOT.TFile.Open(options.file)
	ws=f.Get(options.ws)

	MH=ws.var("MH")
	MH.setVal(options.m)
	hgg_mass=ws.var("CMS_hgg_mass")
	
	for iBin in range(0,options.nBins):
	   for iCat in range(0,options.nCats):
		   print "Going to do Bin%d Cat%d"%(iBin,iCat)
		   pdf=ws.pdf("hggpdfsmrel_8TeV_Bin%d_cat%d"%(iBin,iCat))
		   hgg_mass_=options.low
		   PrintCat=False
		   while hgg_mass_ <= options.high:
			   hgg_mass.setVal(hgg_mass_)
			   a=ROOT.RooArgSet(hgg_mass)
			   if pdf.getVal(a) <= 0:
				   if not PrintCat: 
					   print "Error in pdf Bin%d cat%d:"%(iBin,iCat)
					   print "\t",
					   PrintCat=True
				   print hgg_mass_,

			   hgg_mass_ += options.step
		   if PrintCat: print "" ##new line


