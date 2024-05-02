import sys
import numpy as np
import pandas as pd
import joblib
import ipaddress
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

def Preprocess(dataframe: pd.DataFrame):
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
    """
    Class that wraps a trained sklearn RandomForestClassifier model.
    """
    def __init__(self, rf: RandomForestClassifier = None, sclr: StandardScaler = None):
        self.rf = rf
        self.sclr = sclr

    def __eprint(self, *args, **kwargs):
        """
        Private function to print to sys.stderr
        """
        print(*args, file=sys.stderr, **kwargs)

    def LoadModel(self, fpath: str):
        """
        Function to load trained model via joblib.

        Parameters:
            fpath (string): full path to .joblib file, including file name and extension.
        Returns:
            bool: True if successful, False if unsuccessful.
        """
        rf_load = None
        try:
            rf_load = joblib.load(fpath)
        except FileNotFoundError:
            self.__eprint(f"ERROR: the file \'{fpath}\' was not found.")
            return False
        except:
            self.__eprint(f"ERROR: an unknown error has occured attempting to call \'joblib.load({fpath})\' while loading random forest model.")
            return False
        else:
            self.rf = rf_load
            return True

    def LoadScaler(self, fpath: str):
        """
        Function to load scaler via joblib.

        Parameters:
            fpath (string): full path to .joblib file, including file name and extension.
        Returns:
            bool: True if successful, False if unsuccessful.
        """
        sclr_load = None
        try:
            sclr_load = joblib.load(fpath)
        except FileNotFoundError:
            self.__eprint(f"ERROR: the file \'{fpath}\' was not found.")
            return False
        except:
            self.__eprint(f"ERROR: an unknown error has occured attempting to call \'joblib.load({fpath})\' while loading scaler.")
            return False
        else:
            self.sclr = sclr_load
            return True
    
    def Predict(self, data: pd.DataFrame):
        """
        Predicts the class based on provided dataframe.

        Parameters:
            data (pandas.Dataframe): data to predict.
        Returns:
            ndarray: array of predictions.
        """
        X = data[self.rf.feature_names_in_]
        Y = None

        if self.rf is not None:
            Y = self.rf.predict(X)
        else:
            self.__eprint("ERROR: random forest model is None!")

        return Y