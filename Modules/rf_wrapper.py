import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

class RF_Model:
    def __init__(self, rf = None, sclr = None):
        self.rf = rf

    def LoadModel(self, fpath):
        pass