
from optparse import OptionParser

usage = "usage: %prog [options] fileName"
parser = OptionParser(usage=usage)
#parser.add_option("-f","--dirName"  ,dest='dirName' ,type='string',help="directory on eos root://eoscms///store/...",default="root://eoscms///store/user/amarini/zjets_V00-12")
parser.add_option("-w","--workSpace"  ,dest='ws' ,type='string',help="workspace name. defalut=%default",default="wsig_8TeV")
parser.add_option("-c","--nCat"  ,dest='nCat' ,type='int',help="number of categories. nCat=%default",default=20)
parser.add_option("-b","--nBin"  ,dest='nBin' ,type='int',help="number of Bins at Gen Level. nBin=%default",default=5)
parser.add_option("-m","--mass"  ,dest='mass' ,type='float',help="Mass. mass=%default",default=125)
parser.add_option("-o","--out"  ,dest='out' ,type='string',help="Output File Name=%default",default="matrixes.pdf")

(options,args)=parser.parse_args()

if len(args)<1:
	parser.error("one argument must be provided")

nBin=options.nBin
nCat=options.nCat

if nCat % nBin !=0:
	parser.error("inconsistent number of bin and categories: nCat%nBin!=0.")

fileName=args[0]

import ROOT

print " -> Importing Combine Library <- "
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so")
ROOT.gStyle.SetOptStat(0)

def ConstructMatrix(ws,nBin,mod,m):
	M=ROOT.TH2D("matrix_mod%d"%mod,"mod%d"%mod,nBin,0,nBin,nBin,0,nBin)
	H=ROOT.TH1D("bkg_mod%d"%mod,"bkg_mod%d"%mod,nBin,0,nBin)
	#"hggpdfsmrel_8TeV_Bin5_$CHANNEL"
	#mass_=ws.var("CMS_hgg_mass")
	mass_=ws.var("MH")
	mass2_=ws.var("MH_SM")
	mass_.setVal(m)
	mass2_.setVal(m)
	#argset=ROOT.RooArgSet(mass_);
	for iBin in range(0,nBin):
	   cat=mod*nBin + iBin	
	   for jBin in range(0,nBin):
	        print "Constructing Matrix for Bin=%d and cat=%d . Mod=%d, nBin=%d, iBin=%d"%(jBin,cat,mod,nBin,iBin)
		#pdf=ws.pdf("hggpdfsmrel_8TeV_Bin%d_cat%d_2_norm"%(jBin,cat))
		func=ws.function("hggpdfsmrel_8TeV_Bin%d_cat%d_norm"%(jBin,cat))
		#pdf=ws.pdf("hggpdfsmrel_8TeV_Bin5_cat9_2_norm")
		if func == None:
			print "func","hggpdfsmrel_8TeV_Bin%d_cat%d_norm"%(jBin,cat),"is NULL"
		M.SetBinContent(iBin,jBin, func.getVal()   )	
	   func=ws.function("hggpdfsmrel_8TeV_Bin%d_cat%d_norm"%(nBin,cat))
	   if func == None:
		print "func","hggpdfsmrel_8TeV_Bin%d_cat%d_norm"%(nBin,cat),"is NULL"
	   H.SetBinContent(iBin, H.GetBinContent(iBin) + func.getVal() ) ## bkg
	return (M,H)


colors=[ROOT.kBlue+2,ROOT.kRed+2,ROOT.kGreen+2,ROOT.kOrange,ROOT.kCyan,ROOT.kGreen,ROOT.kBlack]

if __name__=="__main__":
		fRoot=ROOT.TFile.Open(fileName)
		if fRoot == None:
			print "file %s does not exists"%fileName
			parser.print_usage()
			#parser.error("file %s does not exists"%fileName)

		ws = fRoot.Get(options.ws)
		if ws == None:
			print "workspace %s not in file %s"%(options.ws,fileName)
			parser.print_usage()
		C1=ROOT.TCanvas("c1","c1",800,800)
		C2=ROOT.TCanvas("c2","c2",800,800)
		C3=ROOT.TCanvas("c3","c3",800,800)
		AllH=[]
		max1=-1
		max2=-1
		for mod in range(0,nCat/nBin):
			(M,H) = ConstructMatrix(ws,nBin,mod,options.mass)
			#M.SetFillColor(colors[mod])
			M.SetFillStyle(0)
			M.SetLineColor(colors[mod])
			H.SetLineColor(colors[mod])
			AllH.append(H)
			AllH.append(M)
			opt1="BOX"
			opt2="HIST"
			if mod>0 : 
				opt1 += " SAME"
				opt2 += " SAME"
			
			C1.cd()
			M.Draw(opt1)
			max1=max(max1,M.GetMaximum())
			C2.cd()
			H.Draw(opt2)
			max2=max(max2,H.GetMaximum())

			C3.cd()
			R=H.Clone("bkg_ratio_mod%d"%mod)
			K=M.ProjectionX()

			R.Divide(K)
			R.SetLineColor(colors[mod])
			R.SetMaximum(1.0)
			R.SetMinimum(0.0)
			R.Draw(opt2)
			AllH.append(R)


		C1.FindObject("matrix_mod0").SetMaximum(max1*1.2);
		C2.FindObject("bkg_mod0").SetMaximum(max1*1.2);

		basename=options.out[0:options.out.rfind('.')]
		ext=options.out[options.out.rfind('.'):]
		C1.SaveAs(options.out)
		C1.SaveAs(basename + ".root")
		C2.SaveAs(basename + "_2"+ ext )
		C2.SaveAs(basename + "_2"+ ".root" )
		C3.SaveAs(basename + "_3"+ ext )
		C3.SaveAs(basename + "_3"+ ".root" )



