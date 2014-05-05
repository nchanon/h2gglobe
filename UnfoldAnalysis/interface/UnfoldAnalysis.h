
// This class want to provide a general tool that book unfolding histogrmas for globe for each analysis

#include "LoopAll.h"
#include "PhotonAnalysis/interface/StatAnalysis.h"
#include "PhotonAnalysis/interface/MassFactorizedMvaAnalysis.h"
#include <string>

#ifndef UNFOLD_INHERITANCE
#define UNFOLD_INHERITANCE StatAnalysis
#endif


class UnfoldAnalysis: public UNFOLD_INHERITANCE{

public:

//constructor
UnfoldAnalysis():UNFOLD_INHERITANCE(),
//	JetPtForDiffAnalysis(30.),
	doUnfoldHisto(0),
//	nVarCategories(0),
	PhoEtaDiffAnalysis(2.5),
	PhoIsoDiffAnalysis(5),
	PhoIsoDRDiffAnalysis(0.5),
	JetPhoDRDiffAnalysis(0.5)
{
sigProcessesToBook.clear();
PhoPtDiffAnalysis.resize(2);PhoPtDiffAnalysis[0]=40;PhoPtDiffAnalysis[1]=30;
};
//destructor
void Init(LoopAll&);

void bookSignalModel(LoopAll& l, Int_t nDataBins) ;

void FillRooContainer(LoopAll& l, int cur_type, float mass, float diphotonMVA,
        int category, float weight, bool isCorrectVertex, int diphoton_id);

void FillRooContainerSyst(LoopAll& l, const std::string &name, int cur_type,
        std::vector<double> & mass_errors, std::vector<double> & mva_errors,
        std::vector<int> & categories, std::vector<double> & weights, int diphoton_id);

bool Analysis(LoopAll& l, Int_t jentry);

//flags
bool doUnfoldHisto;



// generator cuts -- same as detector cuts

vector<float> PhoPtDiffAnalysis;
float PhoEtaDiffAnalysis;
float PhoIsoDiffAnalysis;
float PhoIsoDRDiffAnalysis;
float JetPhoDRDiffAnalysis;
float JetEtaForDiffAnalysis;

//ineheredit - must not be redeclared, otherwise shadow them

//---- defined in diff analysis
//float JetPtForDiffAnalysis;
//string VarDef;//("pToMscaled");
//vector<int> sigPointsToBook;
//vector<string> sigProcessesToBook ;
//int nVarCategories;
//vector<float> varCatBoundaries;//=0.,20.,35.,60.,130.,400.;
//----------

int computeGenBin(LoopAll &l,int cur_type,int &ig1,int &ig2) ;
int computeGenBin(LoopAll &l,int cur_type) 
	{int ig1,ig2;return computeGenBin(l,cur_type,ig1,ig2);} ;

protected:

//this variables are used ONLY for debug
map<string,float> effGenCut;

};


