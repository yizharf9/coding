
import random

import numpy as np

class LTP:
    def __init__(self):
        self.state = False
        
    def predict(self, input):
        output = self.state
        self.state = input  
        return output

class BMP:
    def __init__(self):
        self.state = (False, False)
        self.state_str = "SNT"
    
    # 11-ST, 10-WT, 01-WNT, 00-SNT
    def predict(self,input):
        # 11-ST
        if self.state == (True, True):
            output = True
            if not input: # -> 10-WT
                self.state = (True, False)
                self.state_str = "WT"

        # 10-WT
        elif self.state == (True, False):
            output = True   
            if not input: # -> 01-WNT
                self.state = (False, True)
                self.state_str = "WNT"
            else:         # -> 11-ST
                self.state = (True, True)
                self.state_str = "ST"

        # 01-WNT
        elif self.state == (False, True):
            output = False
            if input:      # -> 10-WT
                self.state = (True, False)
                self.state_str = "WT"
            else:          # -> 00-SNT
                self.state = (False, False)
                self.state_str = "SNT"

        # 00-SNT
        elif self.state == (False, False):
            output = False
            if input:
                self.state = (False, True)
                self.state_str = "WNT"
        
        return output

class GBMP:
    def __init__(self):
        self.g = False
        self.BHT1 = BMP()
        self.BHT2 = BMP()
    
    def predict(self,input):
        if self.g:
            output = self.BHT1.predict(input)
        else:
            output = self.BHT2.predict(input)
        
        self.g = input
        
        return output

class CorrelatingPredictor:
    def __init__(self):
        self.g = False # Global history (0=False, 1=True)
        
        # BHT for g=0
        self.b1_g0 = LTP()
        self.b2_g0 = LTP()
        
        # BHT for g=1
        self.b1_g1 = LTP()
        self.b2_g1 = LTP()
        
    def predict(self,input1,input2):
        if self.g == False:
            output1 = self.b1_g0.predict(input1)
            output2 = self.b2_g0.predict(input2)
        else:
            output1 = self.b1_g1.predict(input1)
            output2 = self.b2_g1.predict(input2)

        self.g = input
        
        return output1,output2

ltp1 = LTP()
bmp = BMP()
gbmp = GBMP()
correlating_predictor = CorrelatingPredictor()

Y = [18,13,10,11,12,20,27,30,33]
b1_predictions = []
b2_predictions = []

for i in range(len(Y)):
    y = Y[i]
    input1 = y % 2 == 0
    input2 = y % 10 == 0
    
    prediction1,prediction2 = correlating_predictor.predict(input1,input2)
    b1_predictions.append(prediction1)
    b2_predictions.append(prediction2)


print(f"Branch History: {Y}")
print(f"Predictions b1:    {b1_predictions}")
print(f"Predictions b2:    {b2_predictions}")

# N = 10
# branch_history = [random.choice([True, False]) for _ in range(N)]
# predictions = []
# states = []

# for i in range(len(branch_history)):
#     input = branch_history[i]
#     states.append(bmp.state_str)
#     prediction = bmp.predict(input)
#     predictions.append(prediction)


# print(f"Branch History: {branch_history}")
# print(f"Predictions:    {predictions}")
# print(f"States:         {states}")
