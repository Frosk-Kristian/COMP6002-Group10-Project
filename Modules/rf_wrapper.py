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
    out['Destination IP_int'] = out.apply(lambda x: int (ipaddress.IPv4Address(x[' Destination IP'])), axis=1)

    # converts date and time values to UNIX timestamps
    out['UnixTimestamp'] = out.apply(lambda x: (pd.to_datetime(x[' Timestamp'], dayfirst=True).timestamp()), axis=1)

    # drops the original, unmodified columns
    out.drop(columns = [' Source IP', ' Destination IP', ' Timestamp'], inplace = True)

    return out

class RF_Model:
    """
    Class that wraps a fit sklearn GridSearchCV (random forest classifier).
    """
    def __init__(self, gs: GridSearchCV = None, sclr: StandardScaler = None):
        """
        Constructs a RF_Model object.
        """
        self.gs = gs
        self.sclr = sclr
        if self.sclr is not None:
            self.sclr.set_output(transform='pandas') # specifies to return a pandas dataframe

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
        except Exception as e:
            self.__eprint(f"ERROR: an unknown error has occured attempting to call \'joblib.load({fpath})\' during LoadGridSearch().\n", repr(e))
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
        except Exception as e:
            self.__eprint(f"ERROR: an unknown error has occured attempting to call \'joblib.load({fpath})\' while loading scaler.\n", repr(e))
            return False
        else:
            self.sclr = sclr_load
            self.sclr.set_output(transform='pandas') # specifies to return a pandas dataframe
            return True
    
    def __Normalise(self, data: pd.DataFrame):
        """
        Private function that calls self.sclr.transform on a pandas dataframe, and returns the transformed dataframe.

        Parameters:
            data (pd.DataFrame): dataframe to be normalised.
        Returns:
            pd.DataFrame: normalised dataframe.
            None: in the event of an error.
        """
        if self.sclr is not None:
            data_n = data[self.sclr.feature_names_in_] # uses only the feature names seen by the grid search
            try:
                data_n = self.sclr.transform(data_n[data_n.columns])
            except Exception as e:
                self.__eprint(f"ERROR: an unknown error occured calling \'self.sclr.transform(data_n[{data_n.columns}])\' during self.__Normalise()!\n", repr(e))
                return None
            else:
                return data_n
        else:
            self.__eprint("ERROR: scaler is None during self.__Normalise()!")
            return None

    def Predict(self, data: pd.DataFrame, is_scaled: bool = False):
        """
        Predicts the class based on provided dataframe.

        Parameters:
            data (pandas.Dataframe): data to predict.
            is_scaled (bool): whether data has already been normalised, defaults to False.
        Returns:
            ndarray: array of predictions.
            None: in the event of an error.
        """
        X = data.copy(deep=True)
        Y = None

        if is_scaled is False:
            X = self.__Normalise(X)

        if X is not None:
            if self.gs is not None:
                try:
                    X = X[self.gs.feature_names_in_] # uses only the feature names seen by the grid search beyond this point
                    Y = self.gs.predict(X)
                except Exception as e:
                    self.__eprint(f"ERROR: an unknown error occured calling \'self.gs.predict({X})\' during Predict()!\n", repr(e))
                    return None
            else:
                self.__eprint("ERROR: grid search is None!")
        else:
            self.__eprint("ERROR: value of X is None during Predict()!")
        
        return Y

    def PredictProba(self, data: pd.DataFrame, is_scaled: bool = False):
        """
        Predicts the probabilities of each row in a dataframe belonging to each class.

        Parameters:
            data (pandas.Dataframe): data to predict.
            is_scaled (bool): whether data has already been normalised, defaults to False.
        Returns:
            ndarray: array of predictions along with probabilities of each class.
            None: in the event of an error.
        """
        X = data.copy(deep=True)
        Y = None

        if is_scaled is False:
            X = self.__Normalise(X)

        if X is not None:
            if self.gs is not None:
                try:
                    X = X[self.gs.feature_names_in_] # uses only the feature names seen by the grid search beyond this point
                    Y = self.gs.predict_proba(X)
                except Exception as e:
                    self.__eprint(f"ERROR: an unknown error occured calling \'self.gs.predict_proba({X})\' during PredictProba()!\n", repr(e))
                    return None
            else:
                self.__eprint("ERROR: grid search is None!")
        else:
            self.__eprint("ERROR: value of X is None during PredictProba()!")
        
        return Y
