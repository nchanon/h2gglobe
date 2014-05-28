import sys,os
from optparse import OptionParser

usage = "usage: %prog [options] fileName"
parser = OptionParser(usage=usage)
#parser.add_option("-f","--dirName"  ,dest='dirName' ,type='string',help="directory on eos root://eoscms///store/...",default="root://eoscms///store/user/amarini/zjets_V00-12")
parser.add_option("-w","--workSpace"  ,dest='ws' ,type='string',help="workspace name. defalut=wsig_8TeV/cms_hgg_workspace",default="")
parser.add_option("-c","--nCat"  ,dest='nCat' ,type='int',help="number of categories. nCat=%default",default=20)
parser.add_option("-b","--nBin"  ,dest='nBin' ,type='int',help="number of Bins at Gen Level. nBin=%default",default=5)
parser.add_option("-m","--mass"  ,dest='mass' ,type='float',help="Mass. mass=%default",default=125)
parser.add_option("-o","--out"  ,dest='out' ,type='string',help="Output File Name=%default",default="matrixes.pdf")
parser.add_option("-k","--isBinned"  ,dest='isBinned' ,action='store_true',help="isBinned. default=%default",default=False)

(options,args)=parser.parse_args()

if len(args)<1:
	parser.error("one argument must be provided")

nBin=options.nBin
nCat=options.nCat

isBinned=options.isBinned
if isBinned:
	wsName="cms_hgg_workspace"
	if options.ws != "": wsName=options.ws
else:
	wsName="wsig_8TeV"
	if options.ws != "": wsName=options.ws

if nCat % nBin !=0:
	parser.error("inconsistent number of bin and categories: nCat%nBin!=0.")

fileName=args[0]

sys.argv=[]
import ROOT

print " -> Importing Combine Library <- "
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so")
ROOT.gStyle.SetOptStat(0)

def ConstructMatrix(ws,nBin,mod,m,isBinned=False):
	M=ROOT.TH2D("matrix_mod%d"%mod,"mod%d"%mod,nBin,0,nBin,nBin,0,nBin)
	M.GetXaxis().SetTitle("RECO")
	M.GetYaxis().SetTitle("GEN")
	H=ROOT.TH1D("bkg_mod%d"%mod,"bkg_mod%d"%mod,nBin,0,nBin)
	#"hggpdfsmrel_8TeV_Bin5_$CHANNEL"
	#mass_=ws.var("CMS_hgg_mass")
	#argset=ROOT.RooArgSet(mass_);

	if not isBinned:
		mass_=ws.var("MH")
		mass2_=ws.var("MH_SM")
		mass_.setVal(m)
		mass2_.setVal(m)
		for iBin in range(0,nBin):
		   cat=mod*nBin + iBin	
		   for jBin in range(0,nBin):
		        print "Constructing Matrix for Bin=%d and cat=%d . Mod=%d, nBin=%d, iBin=%d"%(jBin,cat,mod,nBin,iBin)
			func=ws.function("hggpdfsmrel_8TeV_Bin%d_cat%d_norm"%(jBin,cat))
			if func == None:
				print "func","hggpdfsmrel_8TeV_Bin%d_cat%d_norm"%(jBin,cat),"is NULL"
			M.SetBinContent(iBin,jBin, func.getVal()   )	
		   func=ws.function("hggpdfsmrel_8TeV_Bin%d_cat%d_norm"%(nBin,cat))
		   if func == None:
			print "func","hggpdfsmrel_8TeV_Bin%d_cat%d_norm"%(nBin,cat),"is NULL"
		   H.SetBinContent(iBin, func.getVal() ) ## bkg
		return (M,H)

	if isBinned:
		for iBin in range(0,nBin):
		   cat=mod*nBin + iBin	
		   for jBin in range(0,nBin):
		        print "Constructing Binned Matrix for Bin=%d and cat=%d . Mod=%d, nBin=%d, iBin=%d"%(jBin,cat,mod,nBin,iBin)
			hist=ws.data("roohist_sig_Bin%d_mass_m%d_cat%d"%(jBin,int(m),cat))
			if hist == None:
				print "hist","roohist_sig_Bin%d_mass_m%d_cat%d"%(jBin,m,cat),"is NULL"
			M.SetBinContent(iBin,jBin, hist.sumEntries()   )	
		   hist=ws.data("roohist_sig_Bin%d_mass_m%d_cat%d"%(nBin,int(m),cat))
		   if hist == None:
			print "hist","roohist_sig_Bin%d_mass_m%d_cat%d"%(jBin,m,cat),"is NULL"
		   H.SetBinContent(iBin, hist.sumEntries() ) ## bkg
		return (M,H)

def GetGenHisto(ws,nBin,m,isBinned=False):
	### TO BE COMPLETED
	if not isBinned: return None
	if isBinned:
		H=ROOT.TH1D("gen","gen",nBin,0,nBin)
		for jBin in range(0,nBin):
			hist=ws.data("roohist_sig_gen_Bin%d_mass_m%d_cat0"%(jBin,int(m) ) )
		   	H.SetBinContent(jBin, hist.sumEntries() ) ## eff
		return H

colors=[ROOT.kBlue+2,ROOT.kRed+2,ROOT.kGreen+2,ROOT.kOrange,ROOT.kCyan,ROOT.kGreen,ROOT.kBlack]

if __name__=="__main__":
		fRoot=ROOT.TFile.Open(fileName)
		if fRoot == None:
			print "file %s does not exists"%fileName
			parser.print_usage()
			#parser.error("file %s does not exists"%fileName)

		ws = fRoot.Get(wsName)
		if ws == None:
			print "workspace %s not in file %s"%(options.ws,fileName)
			parser.print_usage()
		C1=ROOT.TCanvas("c1","c1",800,800)
		C2=ROOT.TCanvas("c2","c2",800,800)
		C3=ROOT.TCanvas("c3","c3",800,800)
		C4=ROOT.TCanvas("c4","c4",800,800)

		L=ROOT.TLegend(0.12,.7,.32,.89)
		
		AllH=[]
		max1=-1
		max2=-1
		for mod in range(0,nCat/nBin):
			(M,H) = ConstructMatrix(ws,nBin,mod,options.mass,isBinned)
			#M.SetFillColor(colors[mod])
			M.SetFillStyle(0)
			M.SetLineColor(colors[mod])
			H.SetLineColor(colors[mod])
			AllH.append(H)
			AllH.append(M)
			L.AddEntry(M,"cat%d"%mod,"F")
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
			R.SetTitle("Efficiency");
			R.GetYaxis().SetTitle("Bkg fraction Efficiency");


			K=M.ProjectionX()
			K.Add(R)

			R.Divide(K)
			R.SetLineColor(colors[mod])
			R.SetMaximum(1.0)
			R.SetMinimum(0.0)
			R.Draw(opt2)
			AllH.append(R)

			if isBinned:
				C4.cd()
				G=GetGenHisto(ws,nBin,options.mass,isBinned);
				J=M.ProjectionY();
				Eff=J.Clone("Eff_ratio_mod%d"%mod);
				Eff.GetYaxis().SetTitle("Efficiencies x Cat");

				Eff.Divide(G);
				Eff.SetLineColor(colors[mod])
				Eff.SetMaximum(1.0)
				Eff.SetMinimum(0.0)
				Eff.Draw(opt2)
				if mod==0 : 
					Tot=Eff.Clone("Eff_ratio_sum")
					Tot.SetLineColor(ROOT.kBlack)
				else:
					Tot.Add(Eff)

				AllH.append(Eff)


		C1.FindObject("matrix_mod0").SetMaximum(max1*1.2);
		C2.FindObject("bkg_mod0").SetMaximum(max1*1.2);
		C1.cd()
		L.Draw()
		C2.cd()
		L.Draw()
		C3.cd()
		L.Draw()


		basename=options.out[0:options.out.rfind('.')]
		ext=options.out[options.out.rfind('.'):]
		C1.SaveAs(options.out)
		C1.SaveAs(basename + ".root")
		C2.SaveAs(basename + "_2"+ ext )
		C2.SaveAs(basename + "_2"+ ".root" )
		C3.SaveAs(basename + "_3"+ ext )
		C3.SaveAs(basename + "_3"+ ".root" )
		if isBinned:
			C4.cd()
			Tot.Draw("SAME")
			L.AddEntry(Tot,"tot","L")
			L.Draw()
			C4.SaveAs(basename + "_4"+ ext )
			C4.SaveAs(basename + "_4"+ ".root" )



