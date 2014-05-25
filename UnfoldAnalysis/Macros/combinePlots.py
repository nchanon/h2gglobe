#!/usr/bin/python
import os,sys
import array
from glob import glob
from subprocess import call
from optparse import OptionParser

##### CONFIGURATION ######
nBins_=6 # later figured out
mass_=125
sigma_=1
wsFile_="CMS-HGG.root"
###      red green, blue, orange,cyan, yelow
colors_=[632,416,600,800,432,400+2,416+2,632+2,58]
dir_='jobs'
##########################

############ PARSER 
if __name__=="__main__":
	usage = "usage: %prog [options]"
	parser=OptionParser(usage=usage)
	parser.add_option("-b","--batch" ,dest='batch',action='store_true',help="Batch Mode. Default=%default",default=False)
	parser.add_option("-D","--dir" ,dest='dir',type='string',help="Directory. Default=%default",default=dir_)
	parser.add_option("-s","" ,dest='sig',type='string',help="Ws Sig not fitted. Default=%default",default=wsFile_)
	parser.add_option("-v","--var" ,dest='var',type='string',help="Variable. If non null read bins from the var file. Default=%default",default="")
	(options,args)=parser.parse_args()
	dir_=options.dir
        wsFile_=options.sig

print "Importing ROOT"
import ROOT
if options.batch: ROOT.gROOT.SetBatch()
ROOT.gROOT.ProcessLine(
		'struct entry{\
		Float_t var;\
		Float_t nll;\
		};'
		)
from ROOT import entry

ROOT.gROOT.ProcessLine("Float_t histBins[100];");
from ROOT import histBins;
import math
from glob import glob
#take from the file
if options.var == "":
	nBins_=6
	histBins[0]=0
	histBins[1]=20
	histBins[2]=35
	histBins[3]=60
	histBins[4]=130
	histBins[5]=400
else:
	wd=os.environ['PWD']
	wd_list=wd.split('/')
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
	nBins_=0
	print "Boundaries ",
	for bound in VarCategoryBoundaries.split(','):
		if bound != "":
			print float(bound),
			histBins[nBins_]=float(bound)
			nBins_ +=1
	print " "
	#nBins_ -= 1 #1bin less than the n. of bondaries



C=ROOT.TCanvas("c","c")
L=ROOT.TLegend(.65,.65,.89,.89)
Mu=[]
Graphs=[] ## keep them otherwise destroyed too soon
print "Going to Scan Bins"
for iBin in range(0,nBins_):
	#open the TTrees
	print "Going to open","%s/MultiDimFit_Bin%d.root"%(dir_,iBin)
	f=ROOT.TFile.Open("%s/MultiDimFit_Bin%d.root"%(dir_,iBin))
	t=f.Get("limit")
	
	#import
	#r_Bin0,deltaNLL
	A=ROOT.entry()

	t.SetBranchAddress("r_Bin%d"%iBin,ROOT.AddressOf(A,'var'))
	t.SetBranchAddress("deltaNLL",ROOT.AddressOf(A,"nll"))
	
	values=[]
	for iEntry in range(0,t.GetEntries()):
		t.GetEntry(iEntry)
		values.append( (A.var,A.nll) )
	values.sort()
	#Get Minimum and errors
	(x,y)=values[0] #var,nll
	for (x1,y1) in values:
		if y1<y: (x,y)=(x1,y1)
	valuesForErrors=[ x1 for (x1,y1) in values if y1<y+0.5*(sigma_**2) ] 

	try:
		e1= min(valuesForErrors)
		e2= max(valuesForErrors)
	except ValueError: e1=e2=-1
	Mu.append( (x,e1,e2) )

	g=ROOT.TGraph()
	g.SetName("Bin%d"%iBin)
	g.SetLineColor(colors_[iBin])
	g.SetFillColor(ROOT.kWhite)
	g.SetLineWidth(2)
	for (x1,y1) in values:
		g.SetPoint(g.GetN(),x1,y1)
	if(iBin==0): 
		g.Draw("AL")	
		g.GetYaxis().SetTitle("#Delta NNL");
		g.GetXaxis().SetTitle("#mu");
	else: g.Draw("L SAME")
	Graphs.append(g)
	L.AddEntry(g,"Bin%d"%iBin,"F")

	f.Close()
L.Draw()
line=ROOT.TGraph()
line.SetName("1sigma")
line.SetPoint(0,-10,0.5)
line.SetPoint(1,10,0.5)
line.Draw("L SAME")
line2=ROOT.TGraph()
line2.SetName("2sigma")
line2.SetPoint(0,-10,2)
line2.SetPoint(1,10,2)
line2.Draw("L SAME")

C.SaveAs("plots_nll_"+dir_.replace("/","")+".pdf")
C.SaveAs("plots_nll_"+dir_.replace("/","")+".root")
#C.SaveAs("plots_nll_"+dir_.replace("/","")+".png")

### Get The Histograms  and normalize to the total xSec

# load combine
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so")
f=ROOT.TFile.Open(wsFile_)
ws=f.Get("cms_hgg_workspace")
 #((RooDataSet*)w->data("sig_gen_Bin2_mass_m125_cat0"))->sumEntries()

nEvents={}
masses=[120,125,130]
for iBin in range(0,nBins_):
   for m in masses:
	nEvents[ (m,iBin)]= ws.data("sig_gen_Bin%d_mass_m%d_cat0"%(iBin,m)).sumEntries();
#interpolation to our mass point
nEventsInterpolated=[]
for iBin in range(0,nBins_):
	mBin=0
	while not (masses[mBin] <= mass_ and mass_ < masses[mBin+1]): mBin+=1	
	y1 = nEvents[ (masses[mBin],iBin) ]
	x1 = masses[mBin]
	y2 = nEvents[ (masses[mBin+1],iBin) ]
	x2 = masses[mBin+1]
	x  = mass_
	m = (y2-y1)/(x2-x1)
	q = y1-m*x1
	nEventsInterpolated.append( m*x+q )
	print "Bin=%d %d<m<%d"%(iBin,masses[mBin],masses[mBin+1]),"events [",y1,y2,"]","inter = ",m*x+q



C2=ROOT.TCanvas("c2","c2")
ROOT.gStyle.SetErrorX(0)
ROOT.gStyle.SetOptStat(0)
H=ROOT.TH1F("h","Data",nBins_-1,histBins);
HErr=ROOT.TH1F("h","Error",nBins_-1,histBins);
HExp=ROOT.TH1F("Expected","Expected",nBins_-1,histBins);
for iBin in range(0,nBins_-1):
	print "Mu ",Mu[iBin][0], "+-", Mu[iBin][1],Mu[iBin][2]
	HExp.SetBinContent(iBin+1,nEventsInterpolated[iBin]/H.GetBinWidth(iBin)* 19.7)
	low=nEventsInterpolated[iBin]/H.GetBinWidth(iBin)* 19.7*Mu[iBin][1]
	high=nEventsInterpolated[iBin]/H.GetBinWidth(iBin)* 19.7*Mu[iBin][2]
	HErr.SetBinContent(iBin+1, (low+high)/2)
	HErr.SetBinError(iBin+1,math.fabs(low-high)/2)
	H.SetBinContent(iBin+1,nEventsInterpolated[iBin]/H.GetBinWidth(iBin)* 19.7*Mu[iBin][0] )
H.SetMarkerStyle(20)
H.Draw("P")
H.GetYaxis().SetTitle("L d#sigma/dP_{T}")
HExp.SetLineColor(ROOT.kRed)
HExp.SetLineWidth(2)
HExp.Draw("HIST SAME")
HErr.Draw("P E SAME")
H.Draw("P SAME")

C2.SaveAs("xSec_"+dir_.replace("/","")+".pdf")
C2.SaveAs("xSec_"+dir_.replace("/","")+".png")
C2.SaveAs("xSec_"+dir_.replace("/","")+".root")
