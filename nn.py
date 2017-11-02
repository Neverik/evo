import random
import math
import numpy as np
import copy

def sigmoid (x):
    return 1/(1 + np.exp(-x))
        
class net (object):
    
    def __init__(self, inputneurons, numlayers, layersdepth, outputneurons):
        self.layers = []
        self.outputneurons = outputneurons
        self.layers.append(np.random.randn(inputneurons,layersdepth))
        for i in range(numlayers-2):
            self.layers.append(np.random.randn(layersdepth,layersdepth))
        self.layers.append(np.random.randn(layersdepth,outputneurons))
    
    def run(self, inputv):
        curinp = [inputv]
        try:
            for i in self.layers:
                curinp = np.dot(curinp,i)
        except:
            return np.zeros(self.outputneurons).tolist()
        return curinp.tolist()[0]
    
    def mutate(self,rate):
        #mutated = np.add(self.layers,np.random.normal(0,rate,np.array(self.layers)))
        return
