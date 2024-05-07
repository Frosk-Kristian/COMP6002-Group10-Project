import pandas as pd
from Modules.rf_wrapper import RF_Model, Preprocess

filepath = "finaldataset.csv"


df = pd.read_csv(filepath)

processed_df = Preprocess(df)
rf_model = RF_Model()

rf_model.Predict(processed_df)

