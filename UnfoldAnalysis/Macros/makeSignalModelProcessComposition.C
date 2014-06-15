
//std
#include <vector>
#include <map>
#include <string>
using namespace std;

//ROOT
#include "TFile.h"
#include "TCanvas.h"
#include "TPave.h"
#include "TH2F.h"
#include "TH1F.h"
#include "TStyle.h"
#include "TROOT.h"


//global
vector<string> procs;
vector<unsigned int> colors;

int StdProcs()
{
	procs.clear();
	procs.reserve(10);
	colors.clear();
	colors.reserve(10);

	procs.push_back("ggh"); colors.push_back(kGreen+2);
	procs.push_back("vbf"); colors.push_back(kRed+2);
	procs.push_back("tth"); colors.push_back(kBlue-4);
	procs.push_back("wh");  colors.push_back(kOrange+2);
	procs.push_back("zh");  colors.push_back(kCyan);

return 0;
}

int makeSignalModelProcessComposition(const char fileName[]="xSec_pToMscaled.root",const char*title="p_{T}")
{
/*
File Content
  KEY: TH1F	data;1	Data
  KEY: TH1F	Expected;1	Expected
  KEY: TH1F	error;1	Error
  KEY: TH1F	HExp_ggh;1	HExpected ggh
  KEY: TH1F	HExp_vbf;1	HExpected vbf
  KEY: TH1F	HExp_wh;1	HExpected wh
  KEY: TH1F	HExp_zh;1	HExpected zh
  KEY: TH1F	HExp_tth;1	HExpected tth
*/

//Load Processes
	StdProcs();
//Fill a map with all the Histos
	map<string,TH1F*> H;
	TFile *fRoot=TFile::Open(fileName);
	for(int iProc=0;iProc<procs.size();++iProc)
	{
	printf("Going to get Histo for %s : %s\n",procs[iProc].c_str(),("HExp_"+procs[iProc]).c_str());
	H[procs[iProc]]=fRoot->Get( ("HExp_"+procs[iProc]).c_str() );
	}
	H["all"]=fRoot->Get("Expected");
	int nBins=H["all"]->GetNbinsX();
// Start Drawing
	TCanvas *c=new TCanvas("c","c",600,600);
	gStyle->SetOptStat(0);
	gStyle->SetOptTitle(0);
	TH2D* dummy = new TH2D("dummy","dummy",1,0,1.,nBins+1,-0.5,nBins+1-.5); // bin Centered in integers
	dummy->Draw("AXIS");
	dummy->GetYaxis()->SetTickLength(0);
	dummy->GetXaxis()->SetTitle("fraction");
//loop oven the bins
	map<int,float> BinStatus;
	for(int iBin=0;iBin<nBins;iBin++)
	   for(int iProc=0;iProc<procs.size();++iProc)
		{
		//create Pave for bin i
		float frac=H[ procs[iProc] ]->GetBinContent(iBin+1) / H["all"]->GetBinContent(iBin+1);
		float x1=BinStatus[iBin];
		float x2=x1+frac;
		float y1=iBin-.2;
		float y2=iBin+.2;
		BinStatus[iBin] += frac; //increment the status
		TPave *pave=new TPave(x1,y1,x2,y2,0);
		printf("Drawing pave for bin %d [%f - %f] and proc %s (%f,%f,%f,%f)\n",iBin,H["all"]->GetBinLowEdge(iBin+1),H["all"]->GetBinLowEdge(iBin+2),procs[iProc].c_str(),x1,y1,x2,y2);
		pave->SetFillColor(colors[iProc]);
		pave->Draw("SAME");
		dummy->GetYaxis()->SetBinLabel(iBin+1,Form("Bin%d",iBin));
		}
//Draw Legend
	for(int iProc=0;iProc<procs.size();++iProc)
		{
		float nProcs=procs.size()+1;
		float x1=(iProc+1)*(1./nProcs)-.02;
		float x2=(iProc+1)*(1./nProcs)+.02;
		float y1=nBins-.15;
		float y2=nBins+.15;
		TPave *pave=new TPave(x1,y1,x2,y2,0);
		pave->SetFillColor(colors[iProc]);
		pave->Draw("SAME");
		TLatex *l=new TLatex();
		l->SetTextFont(42);
		l->SetTextAlign(12);
		l->DrawLatex(x2+0.01,nBins,procs[iProc].c_str());
		
		}
	dummy->Draw("AXIS SAME");
	dummy->Draw("AXIS Y+  SAME");
	TLatex *l=new TLatex();
	l->SetNDC();
	l->SetTextAlign(22);
	l->DrawLatex(0.5,.95,title);
	c->SaveAs( (string("Composition_")+string(fileName)+".pdf" ).c_str());
}
