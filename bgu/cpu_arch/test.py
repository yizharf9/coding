
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
        self.g = False 
        
        # BHT for g=0
        self.b1_g0 = LTP()
        self.b2_g0 = LTP()
        
        # BHT for g=1
        self.b1_g1 = LTP()
        self.b2_g1 = LTP()
        
    def predict(self,input1,input2):
        if self.g == False:
            output1 = self.b1_g0.predict(input1)
        else:
            output1 = self.b1_g1.predict(input1)
        
        self.g = input1
        
        if self.g == False:
            output2 = self.b2_g0.predict(input2)
        else:
            output2 = self.b2_g1.predict(input2)

        self.g = input2
        
        return output1,output2
    
if __name__ == "__main__":

    ltp1 = LTP()
    bmp = BMP()
    gbmp = GBMP()
    correlating_predictor = CorrelatingPredictor()

    Y = [18,13,10,11,12,20,27,30,33]
    b1_predictions = []
    b2_predictions = []
    g = []
    for i in range(len(Y)):
        y = Y[i]
        input1 = y % 2 == 0
        input2 = y % 10 == 0
        
        prediction1,prediction2 = correlating_predictor.predict(input1,input2)
        b1_predictions.append(prediction1)
        b2_predictions.append(prediction2)
        g.append(correlating_predictor.g)


    print(f"Branch History:    {Y}\n")

    print(f"actual b1:         {[y % 2 == 0 for y in Y]}")
    print(f"Predictions b1:    {b1_predictions}")
    correct_b1 = sum([b1_predictions[i] == (Y[i] % 2 == 0) for i in range(len(Y))])
    print(f"Correct b1:        {correct_b1}/{len(Y)}\n")
    
    print(f"g:                 {g}\n")

    print(f"actual b2:         {[y % 10 == 0 for y in Y]}")
    print(f"Predictions b2:    {b2_predictions}")
    correct_b2 = sum([b2_predictions[i] == (Y[i] % 10 == 0) for i in range(len(Y))])
    print(f"Correct b2:        {correct_b2}/{len(Y)}")
