import os
import pandas as pd
from Modules.rf_wrapper import RF_Model, Preprocess


def validate_csv_file(filepath):
    format = filepath.split(".")
    if format[-1] != "csv":
        raise ValueError("Invalid file type!")


if __name__ == "__main__":

    # directories
    data_d = os.getcwd() + r"/Data"
    model_dir = os.getcwd() + r"/Models"
    # files
    sample_fpath = f"{data_d}/finalds_sample.csv"
    # dataframes
    
    validate_csv_file(sample_fpath)

    df = pd.read_csv(sample_fpath)

    # correct naming errors
    df[" Inbound"] = df["Inbound"]
    df[" Label"] = df["Label"]
    df.drop(columns=["Label", "Inbound"], inplace=True)

    # preprocess
    df_p = Preprocess(df)

    # initialise model
    model = RF_Model()
    if model.LoadGridSearch(f"{model_dir}/random_forest.joblib"):
        print("LoadGridSearch() success!")
    if model.LoadScaler(f"{model_dir}/std_scaler.joblib"):
        print("LoadScaler() success!")

    # check for missing features needed by scaler
    sclr_names = model.sclr.feature_names_in_
    print(
        f"WARNING: Labels in Scaler missing from Dataset:\n {list(set(sclr_names).difference(df_p.columns))}"
    )
    print(
        f"WARNING: Labels in Dataset missing from Scaler:\n {list(set(df_p.columns).difference(sclr_names))}"
    )

    to_print = "Feature Order"
    for idx in enumerate(sclr_names):
        to_print += f"\n{idx[0]}:\n Scaler: {idx[1]}\n Dataset: {df_p.drop(columns=[' Label'], inplace=False).columns[idx[0]]}"
    print(to_print)

    # make predictions
    predictions = model.Predict(df_p.drop(columns=[' Label'], inplace=False))
    print(predictions)
