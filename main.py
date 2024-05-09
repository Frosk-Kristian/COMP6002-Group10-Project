import os
import pandas as pd
from Modules.rf_wrapper import RF_Model, Preprocess


def validate_csv_file(filepath):
    format = filepath.split(".")
    if format[-1] != "csv":
        raise ValueError("Invalid file type!")

def NoMissingFeatures(dataframe: pd.DataFrame, rf: RF_Model):
    """
    Function that takes a pandas dataframe and a RF_Model object, checks if the dataframe is missing features the model requires and returns a boolean.

    Parameters:
        dataframe (pd.Dataframe): dataframe to check features of.
        rf (RF_Model): random forest model to check against.
    Returns
        bool: False if the dataset is found to be missing features or an error occurs, else True.
    """
    passed = True

    try:
        sclr_missing = list(set(model.sclr.feature_names_in_).difference(dataframe.columns))
        gs_missing = list(set(model.gs.feature_names_in_).difference(dataframe.columns))

        if sclr_missing:
            print(f"ERROR: dataframe is missing the following features required by model.sclr:\n {sclr_missing}")
            passed = False
        
        if gs_missing:
            print(f"ERROR: dataframe is missing the following features required by model.gs:\n {gs_missing}")
            passed = False
    except Exception as e:
        print(f"ERROR: an unknown error has occured calling \'NoMissingFeatures(dataframe={dataframe}, rf={rf})!\'.\n", repr(e))
        return False
    
    return passed    

def ScalerFeatureIdx(dataframe: pd.DataFrame, rf: RF_Model):
    """
    Function that takes a dataframe and a RF_Model object, and prints the feature found at each index for comparison.

    Parameters:
        dataframe (pd.DataFrame): dataframe to compare.
        rf (RF_Model): random forest model to compare.
    Returns:
        None: no values returned.
    """
    try:
        to_print = "Feature Order"
        sclr_names = rf.sclr.feature_names_in_

        for idx in enumerate(sclr_names):
            to_print += f"\n{idx[0]}:\n Scaler: {idx[1]}\n Dataset: {dataframe.drop(columns=[' Label'], inplace=False).columns[idx[0]]}"
        
        print(to_print)
    except Exception as e:
        print(f"ERROR: an unknown error has occured calling \'ScalerFeatureIdx(dataframe={dataframe}, rf={rf})\'.\n", repr(e))

if __name__ == "__main__":
    # directories
    data_dir = os.getcwd() + r"/Data"
    predict_dir = os.getcwd() + r"/Predictions"
    model_dir = os.getcwd() + r"/Models"
    # files
    syn_fpath = f"{data_dir}/SYN.zip"
    udp_fpath = f"{data_dir}/UDP.zip"
    
    # dataframes
    # df = pd.read_csv(syn_fpath, compression='zip')
    df = pd.read_csv(udp_fpath, compression='zip', nrows=5)

    # correct naming errors
    #df[" Inbound"] = df["Inbound"]
    #df[" Label"] = df["Label"]
    #df.drop(columns=["Label", "Inbound"], inplace=True)
    #df.drop(columns=['Inbound'], inplace=True)

    # preprocess
    df_p = Preprocess(df)

    # initialise model
    model = RF_Model()
    if model.LoadGridSearch(f"{model_dir}/random_forest.joblib"):
        print("LoadGridSearch() success!")
    if model.LoadScaler(f"{model_dir}/std_scaler.joblib"):
        print("LoadScaler() success!")

    if NoMissingFeatures(df_p, model):
        # make predictions
        predictions = model.Predict(df_p)
        print(predictions)
