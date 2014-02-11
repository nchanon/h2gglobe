
from HiggsAnalysis.CombinedLimit.PhysicsModel import *

class UnfoldModel( PhysicsModel ):
	''' Model used to unfold differential distributions '''

	def __init__(self):
		PhysicsModel.__init__(self)
		self.Range=[0.,4]
		self.nBin=4
		self.debug=1

	def setPhysicsOptions(self,physOptions):
		if self.debug>0:print "Setting PhysicsModel Options"
		for po in physOptions:
			if po.startswith("range="):
				self.Range=po.replace("range=","").split(":")
				if len(self.Range)!=2: 
					raise RunTimeError, "Range require minimal and maximal values: range=min:max"
				if self.debug>0:print "new Range is ", self.Range
			if po.startswith("nBin="):
				self.nBin=int(po.replace("nBin=",""))
				if self.debug>0:print "new n. of bins is ",self.nBin

	def doParametersOfInterest(self):
		POIs=""
		if self.debug>0:print "Setting pois"
		for iBin in range(0,self.nBin):
			self.modelBuilder.doVar("r_Bin%d[1,%s,%s]" % (iBin,self.Range[0], self.Range[1]))
			if iBin>0: POIs+=","
			POIs+="r_Bin%d"%iBin
			if self.debug>0:print "Added Bin%d to the POIs"%iBin
		self.modelBuilder.doSet("POI",POIs)
		# --- Higgs Mass as other parameter ----
		if self.options.mass != 0:
		    if self.modelBuilder.out.var("MH"):
		      self.modelBuilder.out.var("MH").removeRange()
		      self.modelBuilder.out.var("MH").setVal(self.options.mass)
		    else:
		      self.modelBuilder.doVar("MH[%g]" % self.options.mass); 
		
	def getYieldScale(self,bin,process):
		if self.debug>1:print "Yield bin=",bin,"process=",process
		if not self.DC.isSignal[process]: return 1
		if process == "Bin%d"%(self.nBin-1): return 1 ## fixed
		if "Bin" in process: return "r_"+process
		elif "bkg_mass" in process: return 1
		else: return "r"

unfoldModel=UnfoldModel()
