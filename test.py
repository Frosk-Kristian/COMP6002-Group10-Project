# program for testing rf_wrapper.py
import os
import pandas as pd
from Modules.rf_wrapper import RF_Model, Preprocess

# set up directories
data_dir = os.getcwd() + r'/Data'
model_dir = os.getcwd() + r'/Models'

# load testing data
X = pd.read_csv((data_dir + '/x_test.csv'), nrows=5)
y = pd.read_csv((data_dir + '/y_test.csv'), nrows=5)

# load model and predict on test data
model = RF_Model()
if model.LoadGridSearch(fpath = (model_dir + 'random_forest.joblib')) is False:
    print("ERROR: LoadGridSearch() was unsuccessful, see stderr.")
else:
    if model.LoadScaler(fpath = (model_dir + 'std_scaler.joblib')) is False:
        print("ERROR: LoadScaler() was unsuccessful, see stderr.")
    else:
        pred = model.Predict(data = X, is_scaled = True)
        print(pred if pred is not None else "ERROR: pred is None!")