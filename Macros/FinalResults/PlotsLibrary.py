#!/usr/bin/python
import os,sys
import array
from glob import glob
from subprocess import call
from optparse import OptionParser

##### CONFIGURATION ######
colors_=[632,416,600,800,432,400+2,416+2,632+2,58]
##########################


print "Importing ROOT"
sys.argv=[]
import ROOT
ROOT.gROOT.SetBatch()

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

def getDet(x=[],y=[],z=[]):
	'''Return determinant of
	 | x[0] y[0] z[0] |
	 | x[1] y[1] z[1] |
	 | x[2] y[2] z[2] |
	'''
	return x[0]*y[1]*z[2] + y[0]*z[1]*x[2] + z[0]*x[1]*y[2] - x[2]*y[1]*z[0] - y[2]*z[1]*x[0] -z[2]*x[1]*y[0] 

import math
def getInterpolation(x=[1,2,3],y=[1,2,3],type='min',value=0.5):
	'''type=min, value'''
	type=type.lower()
	# y= a x**2 + b x + c
	## Cramer
	##  a11 a12 a13 
	##  a21 a22 a23
	##  a31 a32 a33
	Unity=[1,1,1]
	xSquare=[ xx*xx for xx in x ] 

	# | x 1 y | / | x**2 + x + 1 |
	a=  getDet(y,x,Unity)       / getDet(xSquare,x,Unity)
	b=  getDet(xSquare,y,Unity) / getDet(xSquare,x,Unity)
	c=  getDet(xSquare,x,y)     / getDet(xSquare,x,Unity)
	print "--------------------"
	print "(",x[0],",",y[0],")"
	print "(",x[1],",",y[1],")"
	print "(",x[2],",",y[2],")"
	print "a=",a
	print "b=",b
	print "c=",c
	print "val=",value
	print "--------------------"
	
	if type=='min':
		xmin=-b/(2.*a)
		return [ -b/(2.*a), a*(xmin**2)+b*xmin + c ]
	elif type=='val' or type=='value':
		return [ ( -b - math.sqrt(b**2 - 4*a*(c-value) ) ) / (2*a) ,
		  	 ( -b + math.sqrt(b**2 - 4*a*(c-value) ) ) / (2*a) ]
	else: return -9999.



def getMu(nBins=6,dir="jobs",File="UnfoldScanExp",sigma=1,Interpolate=True):
	Mu=[]
	Graphs=[] ## keep them otherwise destroyed too soon
	print "Going to Scan Bins"
	for iBin in range(0,nBins):
		print "Going to open","%s/%sBin%d/%sBin%d.root"%(dir,File,iBin,File,iBin)
		f=ROOT.TFile.Open("%s/%sBin%d/%sBin%d.root"%(dir,File,iBin,File,iBin))
		t=f.Get("limit")
		A=ROOT.entry()
		t.SetBranchAddress("r_Bin%d"%iBin,ROOT.AddressOf(A,'var'))
		t.SetBranchAddress("deltaNLL",ROOT.AddressOf(A,"nll"))
		
		values=[]
		valuesForErrors=[]
		for iEntry in range(0,t.GetEntries()):
			t.GetEntry(iEntry)
			values.append( (A.var,A.nll) )
		values.sort()
		#Get Minimum and errors
		(x,y)=values[0] #var,nll
		for (x1,y1) in values:
			if y1<y: (x,y)=(x1,y1)

		valuesForErrors=[ x1 for (x1,y1) in values if y1<y+0.5*(sigma**2) ] 

		try:
			e1= min(valuesForErrors)
			e2= max(valuesForErrors)
		except ValueError: e1=e2=-1

		print "(",x,",",y," - ",e1,",",e2,")"

		if Interpolate:	
			#remove duplicates
			values=list(set(values))
			values.sort()
			##get minimum
			(xmin,ymin) =values[0]
			for i in range(0, len(values) ):
				(xi,yi)=values[i]
				if yi<ymin:
					ymin=yi
					#assuming i-1,i+1 exists, and sorted otherwise far from min
					xI=(values[i][0],values[i-1][0],values[i+1][0])
					yI=(values[i][1],values[i-1][1],values[i+1][1])
					#print "i=",i,"xI=",xI,"yI=",yI
			print "--- min ---"
			(x,y)=getInterpolation(xI,yI,'min')

			#1 -> if i_min>1 use the  -1 i +1, otherwise use the first three
			e1=values[0][0]
			e2=values[-1][0]

			Ifailed=False
			for i in reversed(range(1, len(values)-1 ) ):
				(xi,yi)=values[i]
				if yi < y + 0.5*sigma**2:
					xI=(values[i][0],values[i-1][0],values[i+1][0])
					yI=(values[i][1],values[i-1][1],values[i+1][1])
					try:
					   print "--- e1 ---"
					   e1=getInterpolation(xI,yI,'val',y+ 0.5*sigma**2)[0]
					except:
					   Ifailed=True
			if Ifailed:
				print "->Interpolation failed"
			Ifailed=False
			for i in range(1, len(values)-1 ) :
				(xi,yi)=values[i]
				if yi < y + 0.5*sigma**2:
					xI=(values[i][0],values[i-1][0],values[i+1][0])
					yI=(values[i][1],values[i-1][1],values[i+1][1])
					try:
					   print "--- e2 ---"
					   e2=getInterpolation(xI,yI,'val',y+ 0.5*sigma**2)[1]
					except:
					   Ifailed=True
			if Ifailed:
				print "->Interpolation failed"

		print "-> (",x,",",y," - ",e1,",",e2,")"
		
		#######
		Mu.append( (x,e1,e2) )
		#######
	
		g=ROOT.TGraph()
		g.SetName("Bin%d"%iBin)
		g.SetLineColor(colors_[iBin])
		g.SetFillColor(ROOT.kWhite)
		g.SetLineWidth(2)
		for (x1,y1) in values:
			g.SetPoint(g.GetN(),x1,y1)
		Graphs.append(g)
	
		f.Close()

	return (Mu,Graphs)


def DrawNLL(dir="jobs",nBins=6,File="UnfoldScanExp"):
	C=ROOT.TCanvas("c","c")
	L=ROOT.TLegend(.65,.65,.89,.89)
	(Mu,Graphs) = getMu(nBins,dir,File)
	for iG in range(0,len(Graphs)):
		g=Graphs[iG]
		if(iG==0): 
			g.Draw("AL")	
			g.GetYaxis().SetTitle("#Delta NNL");
			g.GetXaxis().SetTitle("#mu");
		else: g.Draw("L SAME")
		L.AddEntry(g,"Bin%d"%iG,"F")
	
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

	#vertical lines
	obj=[]
	for iBin in range(0,nBins):
		l_e0=ROOT.TGraph()
		l_e0.SetName("e0_Bin%d"%iBin)
		l_e0.SetPoint(0,Mu[iBin][0],0)
		l_e0.SetPoint(1,Mu[iBin][0],2)

		l_e1=ROOT.TGraph()
		l_e1.SetName("e1_Bin%d"%iBin)
		l_e1.SetPoint(0,Mu[iBin][1],0)
		l_e1.SetPoint(1,Mu[iBin][1],2)

		l_e2=ROOT.TGraph()
		l_e2.SetName("e2_Bin%d"%iBin)
		l_e2.SetPoint(0,Mu[iBin][2],0)
		l_e2.SetPoint(1,Mu[iBin][2],2)

		l_e0.SetLineColor(Graphs[iBin].GetLineColor())
		l_e1.SetLineColor(Graphs[iBin].GetLineColor())
		l_e2.SetLineColor(Graphs[iBin].GetLineColor())

		l_e0.Draw("L SAME")
		l_e1.Draw("L SAME")
		l_e2.Draw("L SAME")
		obj.extend([l_e0,l_e1,l_e2])

	if 'Unfold' in File:
		C.SaveAs("plots_nll_"+dir.replace("/","")+".pdf")
		C.SaveAs("plots_nll_"+dir.replace("/","")+".png")
		C.SaveAs("plots_nll_"+dir.replace("/","")+".root")
	else:
		C.SaveAs("plots_nllreco_"+dir.replace("/","")+".pdf")
		C.SaveAs("plots_nllreco_"+dir.replace("/","")+".png")
		C.SaveAs("plots_nllreco_"+dir.replace("/","")+".root")


def GetXsecSplines():
	#load LoopAll -> Normalization
	(mypath,globe_name)=findPath()
	print "Loading Globe: ",mypath+"/"+"/"+"libLoopAll.so"
	ROOT.gSystem.Load(mypath+"/"+"libLoopAll.so")
	
	#didn't found a more elegant way
	ROOT.gROOT.ProcessLine("struct array { \
			double val[1023]; } ; ")
	
	sqrts_=8
	norm = ROOT.Normalization_8TeV();
	norm.Init(sqrts_);
	brGraph = norm.GetBrGraph(); # TGraph
	brSpline=ROOT.TSpline3("brSpline",brGraph)
	
	procs = [ "ggh","vbf","wh","zh","tth" ]
	xsGraphs = {}
	for proc in procs:
		xsGraph = norm.GetSigmaGraph(proc);
		xsGraphs[proc]=xsGraph
	
	xsGraphs["tot"] = xsGraphs["ggh"].Clone("tot")
	for proc in procs:
		if proc=="ggh": continue # it is cloned in the initialization
	        nPoints=xsGraphs["tot"].GetN()
	        for iP in range(0,nPoints):
			x=ROOT.array()
			y=ROOT.array()
			xsGraphs["tot"].GetPoint(iP,x.val,y.val);
			y.val[0]+=xsGraphs[proc].Eval(x.val[0]);
			xsGraphs["tot"].SetPoint(iP,x.val[0],y.val[0]);
	
	xsSpline=ROOT.TSpline3("xsSpline",xsGraphs["tot"])
	return (xsGraphs,xsSpline,brGraph,brSpline)

def GetXsec(ws,mh,nBins,Lumi):
	(xsGraphs,xsSpline,brGraph,brSpline) = GetXsecSplines()
	nEvents={}
	Xsec=[]
	masses=[120,125,130]
	for iBin in range(0,nBins):
	   eaGraph=ROOT.TGraph()
	   eaGraph.SetName("effAcc")
	   for m in masses:
		nEvents[ (m,iBin)]= ws.data("sig_gen_Bin%d_mass_m%d_cat0"%(iBin,m)).sumEntries();
		xSec=xsGraphs["tot"].Eval(m,xsSpline) *1000.  #pb->fb 
		br=brGraph.Eval(m,brSpline)
		effAcc= ( nEvents[ (m,iBin)]/ ( Lumi* xSec * br )  );
		eaGraph.SetPoint(eaGraph.GetN(), m , effAcc)
	   eaSpline=ROOT.TSpline3("eaSpline",eaGraph)

	   Xsec.append( xsGraphs["tot"].Eval(mh,xsSpline)*1000. * brGraph.Eval(mh,brSpline) * eaGraph.Eval(mh,eaSpline))
	return Xsec
