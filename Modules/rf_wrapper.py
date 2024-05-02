import numpy as np
import pandas as pd
import joblib
import ipaddress
from sklearn.ensemble import RandomForestClassifier

def Preprocess(dataframe):
    """
    Function that performs equivalent preprocessing steps on a dataframe to what was performed in training.

    Parameters:
        dataframe (pandas.DataFrame): unprocessed dataframe.
    Returns:
        pandas.DataFrame: processed dataframe if successful.
        None: if error.
    """
    out = dataframe.copy(deep = True)

    # converts IP addresses to integers
    out['Source IP_int'] = out.apply(lambda x: int (ipaddress.IPv4Address(x[' Source IP'])), axis=1)
    out['Destination IP_int'] = out.apply(lambda x: int (ipaddress.IPv4Address(x[' Source IP'])), axis=1)

    # converts date and time values to UNIX timestamps
    out['UnixTimestamp'] = out.apply(lambda x: (pd.to_datetime(x[' Timestamp']).timestamp()), axis=1)

    # drops the original, unmodified columns
    out.drop(columns = [' Source IP', ' Destination IP', ' Timestamp'], inplace = True)

    return out

class RF_Model:
    def __init__(self, rf = None, sclr = None):
        self.rf = rf

    def LoadModel(self, fpath):
        pass