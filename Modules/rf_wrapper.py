import sys
import numpy as np
import pandas as pd
import joblib
import ipaddress
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV

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
    Class that wraps a fit sklearn GridSearchCV (random forest classifier).
    """
    def __init__(self, gs: GridSearchCV = None, sclr: StandardScaler = None):
        self.gs = gs
        self.sclr = sclr

    def __eprint(self, *args, **kwargs):
        """
        Private function to print to sys.stderr
        """
        print(*args, file=sys.stderr, **kwargs)

    def LoadGridSearch(self, fpath: str):
        """
        Function to load a fit GridSearchCV via joblib.

        Parameters:
            fpath (string): full path to .joblib file, including file name and extension.
        Returns:
            bool: True if successful, False if unsuccessful.
        """
        gs_load = None
        try:
            gs_load = joblib.load(fpath)
        except FileNotFoundError:
            self.__eprint(f"ERROR: the file \'{fpath}\' was not found.")
            return False
        except:
            self.__eprint(f"ERROR: an unknown error has occured attempting to call \'joblib.load({fpath})\' during LoadGridSearch().")
            return False
        else:
            self.gs = gs_load
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
            None: in the event of an error.
        """
        X = data[self.gs.feature_names_in_]
        Y = None

        if self.sclr is not None:
            try:
                X = self.sclr.transform(X[X.columns])
            except:
                self.__eprint(f"ERROR: an unknown error occured calling \'self.sclr.transform(X[{X.columns}])\' during Predict().")
            else:
                if self.gs is not None:
                    Y = self.gs.predict(X)
                else:
                    self.__eprint("ERROR: random forest model is None!")
        else:
            self.__eprint("ERROR: scaler is None!")

        return Y