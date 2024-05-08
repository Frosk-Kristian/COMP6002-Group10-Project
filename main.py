import os
import pandas as pd
from Modules.rf_wrapper import RF_Model, Preprocess

data_d = os.getcwd() + r"/Data"
models_d = os.getcwd() + r"/Models"

sample_fpath = f"{data_d}/finalds_sample.csv"


df = pd.read_csv(sample_fpath)

df[' Inbound'] = df['Inbound']
df[' Label'] = df['Label']
df.drop(columns=['Label', 'Inbound'], inplace=True)

df_p = Preprocess(df)

model_dir = os.getcwd() + r'/Models'

model = RF_Model()

if model.LoadGridSearch(f'{model_dir}/random_forest.joblib'):
    print("LoadGridSearch() success!")

if model.LoadScaler(f'{model_dir}/std_scaler.joblib'):
    print("LoadScaler() success!")

sclr_names = model.sclr.feature_names_in_

print(f"Labels in Scaler missing from Dataset:\n {list(set(sclr_names).difference(df_p.columns))}")
print(f"Labels in Dataset missing from Scaler:\n {list(set(df_p.columns).difference(sclr_names))}")

predictions = model.Predict(df_p.drop(columns=[' Label'], inplace=False))
print(predictions)