import sys
import numpy as np
import pandas as pd
import joblib
import ipaddress
from sklearn.ensemble import RandomForestClassifier

def Preprocess(dataframe):
    """
    Function that performs (relevant) equivalent preprocessing steps on a dataframe to what was performed in training.

    Parameters:
        dataframe (pandas.DataFrame): unprocessed dataframe.
    Returns:
        pandas.DataFrame: processed dataframe.
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
        self.sclr = sclr

    def __eprint(self, *args, **kwargs):
        """
        Function to print to sys.stderr
        """
        print(*args, file=sys.stderr, **kwargs)

    def LoadModel(self, fpath):
        """
        Function to load a trained model via joblib.

        Parameters:
            fpath (string): full path to .joblib file, including file name and extension.
        Returns:
            True: if successful.
            False: if unsuccessful.
        """
        rf_load = None
        try:
            rf_load = joblib.load(fpath)
        except FileNotFoundError:
            self.__eprint(f"ERROR: the file \'{fpath}\' was not found.")
        except:
            self.__eprint(f"ERROR: an unknown error has occured attempting to call \'joblib.load({fpath})\'")
            return False
        else:
            self.rf = rf_load
        
        return True

    def LoadScaler(self, fpath):
        pass