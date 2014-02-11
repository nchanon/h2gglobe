#include "UnfoldAnalysis/interface/UnfoldAnalysis.h"


// -------------------------------------------------------------------------------------------
void UnfoldAnalysis::Init(LoopAll&l){
UNFOLD_INHERITANCE::Init(l);

cout<<"----------------------------------------------------------------------------------------------------"<<endl;
cout<<"Unfold Analysis"<<endl;
cout<<"----------------------------------------------------------------------------------------------------"<<endl;
cout<<"doUnfoldHisto="<<doUnfoldHisto<<endl;
cout<<endl;
cout <<"PhoPtDiffAnalysis="<<PhoPtDiffAnalysis[0];
	if (PhoPtDiffAnalysis.size() >1) cout<< ","<<PhoPtDiffAnalysis[1];
	cout<<endl;
cout<<"PhoEtaDiffAnalysis="    <<PhoEtaDiffAnalysis<<endl;
cout<<"PhoIsoDiffAnalysis="    <<PhoIsoDiffAnalysis<<endl;
cout<<"PhoIsoDRDiffAnalysis="  <<PhoIsoDRDiffAnalysis<<endl;
cout<<"JetPhoDRDiffAnalysis="  <<JetPhoDRDiffAnalysis<<endl;
cout<<"JetEtaForDiffAnalysis=" <<JetEtaForDiffAnalysis<<endl;
cout<<"JetPtForDiffAnalysis="  <<JetPtForDiffAnalysis<<endl;
cout<<"VarDef="                <<VarDef<<endl;
cout<<"nVarCategories="        <<nVarCategories<<endl;
cout<<"varCatBoundaries=";
for(int i=0;i<varCatBoundaries.size();i++)cout<<varCatBoundaries[i]<<",";
	cout<<endl;

cout<<"----------------------------------------------------------------------------------------------------"<<endl;

}



// -------------------------------------------------------------------------------------------
void UnfoldAnalysis::bookSignalModel(LoopAll& l, Int_t nDataBins) 
{

    UNFOLD_INHERITANCE::bookSignalModel(l,nDataBins);

   //check if you have a simple map between bins and categories
   if( nCategories_%nVarCategories )
	{
	cout<<"nCategories %% nVarCategories !=0 ["<<nCategories_<<","<<nVarCategories<<"]"<<endl;
	cout<<"      *** mapping not supported ***"<<endl;
	assert (0);
	}

	//l.rooContainer->verbosity_=true;
    for(size_t isig=0; isig<sigPointsToBook.size(); ++isig) {
        int sig = sigPointsToBook[isig];
	if (doUnfoldHisto) // here: don't care about sigProc
		{
		//for(int iCat=0;iCat<nCategories_/nVarCategories;iCat++)
		//for(int iCat=0;iCat<nCategories_;iCat++)
		for(int iBin=0;iBin<= nVarCategories;iBin++)
			{
			//should be used for syst
			l.rooContainer->CreateDataSet("CMS_hgg_mass",Form("sig_Bin%d_mass_m%d",iBin,sig),nDataBins);
			//signal model for right and wrong vertex
			l.rooContainer->CreateDataSet("CMS_hgg_mass",Form("sig_Bin%d_mass_m%d_rv",iBin,sig),nDataBins);
			l.rooContainer->CreateDataSet("CMS_hgg_mass",Form("sig_Bin%d_mass_m%d_wv",iBin,sig),nDataBins);
			}
			cout<<endl;
		//genLevel Histograms -
		// book only 1 cat
		l.rooContainer->SetNCategories(1);
		for(int iBin=0;iBin<= nVarCategories;iBin++)
			{
			l.rooContainer->CreateDataSet("CMS_hgg_mass",Form("sig_gen_Bin%d_mass_m%d",iBin,sig),nDataBins);
			}
			cout<<endl;
		l.rooContainer->SetNCategories(nCategories_);
		}
	}
	//l.rooContainer->verbosity_=false;
    // Make more datasets representing Systematic Shifts of various quantities
    for(size_t isig=0; isig<sigPointsToBook.size(); ++isig) {
        int sig = sigPointsToBook[isig];
		for(int iBin=0;iBin<= nVarCategories;iBin++){
		   // sig_Bin%d_mass_m%d
		l.rooContainer->MakeSystematics("CMS_hgg_mass",Form("sig_Bin%d_mass_m%d",iBin,sig),-1);
	    }//end loop sigProcess
    }//end for sigPointsToBook

    //I use TH1F instead of TNamed, so they know how to merge files and so on
    TH1F *n=new TNamed("VarDef",VarDef.c_str(),1,0,1);
    l.rooContainer->AppendTH1F("VarDef",n);
    string boundaries="";
    for(int i=0;i<varCatBoundaries.size();i++)
	    boundaries += Form(",%.1f",varCatBoundaries[i]);
    TH1F *n2=new TNamed("varCatBoundaries",boundaries.c_str(),1,0,1);
    l.rooContainer->AppendTH1F("varCatBoundaries",n2);
}


// -------------------------------------------------------------------------------------------
void UnfoldAnalysis::FillRooContainer(LoopAll& l, int cur_type, float mass, float diphotonMVA,
        int category, float weight, bool isCorrectVertex, int diphoton_id)
{

UNFOLD_INHERITANCE::FillRooContainer(l,cur_type,mass,diphotonMVA,category,weight,isCorrectVertex,diphoton_id);

//category w/ observables bins folded in
//int sub_cat=category/nVarCategories;
int bin=-1;

//figure out gen bin: gen selection

if (doUnfoldHisto)
	{
	bin= computeGenBin(l,cur_type)	;
	if ( bin<0 ) bin=nVarCategories;
	
	//all 
	l.rooContainer->InputDataPoint(Form("sig_Bin%d_mass_m%.0f",bin,l.normalizer()->GetMass(cur_type) ),category, mass ,weight);
	//rv and wv
	if(isCorrectVertex)l.rooContainer->InputDataPoint(Form("sig_Bin%d_mass_m%.0f_rv",bin,l.normalizer()->GetMass(cur_type) ),category, mass ,weight);
	else l.rooContainer->InputDataPoint(Form("sig_Bin%d_mass_m%.0f_wv",bin,l.normalizer()->GetMass(cur_type) ),category, mass ,weight);
	}//end doUnfoldHisto

}

// -------------------------------------------------------------------------------------------
void UnfoldAnalysis::FillRooContainerSyst(LoopAll& l, const std::string &name, int cur_type,
        std::vector<double> & mass_errors, std::vector<double> & mva_errors,
        std::vector<int> & categories, std::vector<double> & weights, int diphoton_id)
{
UNFOLD_INHERITANCE::FillRooContainerSyst(l,name,cur_type,mass_errors,mva_errors,categories,weights,diphoton_id);
//should I add something here? 
if (cur_type <0 ){
	int bin=computeGenBin(l,cur_type);
	if (bin<0) bin=nVarCategories;
	int sig=l.normalizer()->GetMass(cur_type) ;
        l.rooContainer->InputSystematicSet( Form("sig_Bin%d_mass_m%d",bin,sig),name,categories,mass_errors,weights);
	}
}

int UnfoldAnalysis::computeGenBin(LoopAll &l,int cur_type,int &ig1,int &ig2){

int is_bkg=-1;
ig1=-1;ig2=-1;

//effGenCut["TOT"]+=1; //DEBUG

//if( effGenCut["TOT"] >100) //DEBUG
//	{
//	cout<<" -- EFF Gen Cuts:"<<effGenCut["TOT"]<<": "<<effGenCut["Full"]/effGenCut["TOT"]
//		 <<" | H "<<effGenCut["Higgs"]/effGenCut["TOT"]
//		 <<" | P "<<effGenCut["pho"]/effGenCut["Higgs"]
//		 <<" | B "<<effGenCut["Full"]/effGenCut["pho"]
//		<<endl;
//	}

if(cur_type>=0) return is_bkg; //no gen for bkg & data

//loop over the gen particles
map<float,int,std::greater<float> > phoHiggs;

for(int igp=0;igp< l.gp_n ;igp++)
   {
   if ( l.gp_status[igp] != 1) continue;
   if ( l.gp_pdgid[igp] != 22 ) continue;
   //find a 25 in the full mother chain
   bool isHiggsSon=false;
   for( int mother=l.gp_mother[igp]; mother>=0 && mother != l.gp_mother[mother]  ;mother=l.gp_mother[mother])
           {
           if (l.gp_pdgid[mother] == 25) isHiggsSon=true;
           }
   if( !isHiggsSon) continue;
   phoHiggs[ ((TLorentzVector*)l.gp_p4->At(igp))->Pt() ]=igp;
   }
if( phoHiggs.size()<2) return is_bkg; // higgs photons does not exist

//effGenCut["Higgs"]+=1;//DEBUG

//map is already sorted
map<float,int,std::greater<float> >::iterator iPho=phoHiggs.begin();
int pho1=iPho->second;
iPho++;
int pho2=iPho->second;

ig1=pho1;ig2=pho2;

TLorentzVector g1=*((TLorentzVector*)l.gp_p4->At(pho1));
TLorentzVector g2=*((TLorentzVector*)l.gp_p4->At(pho2));
//particle level higgs definition
TLorentzVector Hgg = g1+g2;

//cut on photon pt

assert(PhoPtDiffAnalysis.size()>0);

if( g1.Pt() < PhoPtDiffAnalysis[0] ) return is_bkg;

if(PhoPtDiffAnalysis.size()>1)
	if( g2.Pt() < PhoPtDiffAnalysis[1]) return is_bkg;
else // if only one put equal to the first photon pt cut
	if( g2.Pt() < PhoPtDiffAnalysis[0] ) return is_bkg;

 //compute isolation for photons
float pho1Iso=0,pho2Iso=0;
for(int igp=0;igp< l.gp_n ;igp++)
        {
        if ( l.gp_status[igp] != 1) continue;
        if ( l.gp_pdgid[igp] == 12 || l.gp_pdgid[igp]==14 || l.gp_pdgid[igp]==16) continue; //neutrinos
        if ( g1.DeltaR( *((TLorentzVector*)(l.gp_p4->At(igp))) ) < PhoIsoDRDiffAnalysis && pho1 !=igp ) pho1Iso += ((TLorentzVector*)(l.gp_p4->At(igp)))->Pt();
        if ( g2.DeltaR( *((TLorentzVector*)(l.gp_p4->At(igp))) ) < PhoIsoDRDiffAnalysis && pho2 !=igp ) pho1Iso += ((TLorentzVector*)(l.gp_p4->At(igp)))->Pt();
        }
//they are matched to the higgs, so I don't need to consider more photons if not pass the preselection

if(pho1Iso >= PhoIsoDiffAnalysis || pho2Iso >= PhoIsoDiffAnalysis) return is_bkg;

//effGenCut["pho"]+=1;//DEBUG
//redo matching with configurables parameters GEN->RECO TODO - very small corrections ~1./1000 000

//jets
float Ht=0;
int nJets=0;
map<float,int,std::greater<float> > jets;

for(int iJet=0 ;iJet<l.genjet_algo1_n;iJet++)
	{
	if (  ((TLorentzVector*)l.genjet_algo1_p4->At(iJet) )->Pt() < JetPtForDiffAnalysis ) continue;
	if (  fabs(((TLorentzVector*)l.genjet_algo1_p4->At(iJet) )->Eta() )> JetEtaForDiffAnalysis ) continue;
	//DR Cut wrt photons
	if ( ((TLorentzVector*)l.genjet_algo1_p4->At(iJet) )->DeltaR(g1) < JetPhoDRDiffAnalysis  ) continue;
	if ( ((TLorentzVector*)l.genjet_algo1_p4->At(iJet) )->DeltaR(g2) < JetPhoDRDiffAnalysis  ) continue;
	
	//GEN JET is good
	float pt=((TLorentzVector*)l.genjet_algo1_p4->At(iJet))->Pt();
	Ht+=pt;
	nJets+=1;
	jets[ pt ] = iJet;
	}

//compute variable
float var=-1;
if( VarDef=="pToMscaled")
	{
	var=Hgg.Pt()*125./Hgg.M();	
	}
else if( VarDef=="pT")
	{
	var=Hgg.Pt();
	} 
else if( VarDef=="Ygg")
	{
	var=Hgg.Rapidity();
	} 
else if( VarDef=="CosThetaStar")
	{
	var=getCosThetaCS(g1,g2,l.sqrtS);
	} 
else if ( VarDef=="dPhi")
	{
	var=fabs(g1.DeltaPhi(g2));
	}
else if ( VarDef == "Njets")
	{
	var=nJets;
	}
else if ( VarDef == "LeadJetpT")
	{
	if (nJets>0)
	var = ((TLorentzVector*)l.genjet_algo1_p4->At(jets.begin()->second))->Pt();
	else 
	var = -1;
	}
else if (VarDef == "dPhijj")
	{
	if (nJets >1)
		{
		TLorentzVector j1=*((TLorentzVector*)l.genjet_algo1_p4->At(jets.begin()->second));
		TLorentzVector j2=*((TLorentzVector*)l.genjet_algo1_p4->At( (jets.begin()++)->second));
		
		var= fabs(j1.DeltaPhi(j2));
		}
	else
		var=-1;
	}
else if (VarDef == "Mjj")
	{
	if (nJets >1)
		{
		TLorentzVector j1=*((TLorentzVector*)l.genjet_algo1_p4->At(jets.begin()->second));
		TLorentzVector j2=*((TLorentzVector*)l.genjet_algo1_p4->At( (jets.begin()++)->second));
		
		var= (j1+j2).M(); 
		}
	else
		var=-1;
	}
else if ( VarDef == "dPhiggjj")
	{
	if (nJets >1)
		{
		TLorentzVector j1=*((TLorentzVector*)l.genjet_algo1_p4->At(jets.begin()->second));
		TLorentzVector j2=*((TLorentzVector*)l.genjet_algo1_p4->At( (jets.begin()++)->second));
		
		var=  fabs(Hgg.DeltaPhi(j1+j2));
		}
	else
		var=-1;
	}
else if ( VarDef == "Zepp" )
	{
	if (nJets >1)
		{
		TLorentzVector j1=*((TLorentzVector*)l.genjet_algo1_p4->At(jets.begin()->second));
		TLorentzVector j2=*((TLorentzVector*)l.genjet_algo1_p4->At( (jets.begin()++)->second));
		var=fabs(Hgg.Eta() - 0.5*(j1.Eta() + j2.Eta()));
		}
	else
		var = -1;
	}
else if ( VarDef == "dEtajj")
	{
	if (nJets >1)
		{
		TLorentzVector j1=*((TLorentzVector*)l.genjet_algo1_p4->At(jets.begin()->second));
		TLorentzVector j2=*((TLorentzVector*)l.genjet_algo1_p4->At( (jets.begin()++)->second));
		var=fabs(j1.Eta() - j2.Eta());
		}
	else
		var = -1;
	}
else assert( 0  ); //variable not found

int bin=is_bkg;

assert( nVarCategories = varCatBoundaries.size()-1 );

for(int iBin=0;iBin<nVarCategories;iBin++)
	if( varCatBoundaries[iBin] <= var && var< varCatBoundaries[iBin+1] ) bin=iBin;	

//if(bin>=0)effGenCut["Full"]+=1; //DEBUG

return bin ;
}

// -------------------------------------------------------------------------------------------
bool UnfoldAnalysis::Analysis(LoopAll& l, Int_t jentry){

bool r=UNFOLD_INHERITANCE::Analysis(l,jentry);
int cur_type = l.itype[l.current];
//--- exit if not needed
if (cur_type >= 0) return r;
bool isToBook=false;
for(int i=0 ;i<sigPointsToBook.size();i++) if(int(sigPointsToBook[i])==int(l.normalizer()->GetMass(cur_type) )) isToBook=true;

if(!isToBook) return r;
//-----

int g1,g2;
int bin=computeGenBin(l,cur_type,g1,g2);

if (bin>0 && doUnfoldHisto && g1>0 && g2>0 ){
	float HiggsPt= ( *((TLorentzVector*)l.gp_p4->At(g1)) + *((TLorentzVector*)l.gp_p4->At(g2)) ).Pt();
	// VERY VERBOSE
	cout<<" Going to Fill: << Bin:"<<bin<<" mass:"<<l.normalizer()->GetMass(cur_type)<<" weight:"<<(float)l.sampleContainer[l.current_sample_index].weight() * PtReweight(HiggsPt,cur_type) <<endl;
	l.rooContainer->InputDataPoint(Form("sig_gen_Bin%d_mass_m%d",bin,int(l.normalizer()->GetMass(cur_type)) ), 0 ,l.normalizer()->GetMass(cur_type) , (float)l.sampleContainer[l.current_sample_index].weight() * PtReweight(HiggsPt,cur_type) );
	}
//implementation of gen level histograms
return r;
}
