# COMP6002-Group10-Project
## Table of Contents
* [Introduction](#introduction)
* [Cloning](#clone-this-repo)
* [Requirements](#requirements)
* [Files & Directories](#files--directories)

## Introduction
Project utilising a trained model produced in [COMP6002-Group10-Models](https://github.com/Frosk-Kristian/COMP6002-Group10-Models).

## Clone this repo
To clone this repository, run the following:
```shell
git clone https://github.com/Frosk-Kristian/COMP6002-Group10-Project.git
```

## Requirements
Library versions outlined in [requirements.txt](requirements.txt), to install correct versions run:
```shell
pip install -r requirements.txt
```

## Files & Directories
* [AttackSimulation](AttackSimulation): subdirectory containing all files used to generate simulated network traffic, self contained and does not rely on anything external to this subdirectory.
    * [Controller_Updated](AttackSimulation/Controller_Updated):
        * [Benign_Traffic_Collector.py](AttackSimulation/Controller_Updated/Benign_Traffic_Collector.py): Python script to capture and write packets to a .csv file.
        * [DDoS_Traffic_Collector.py](AttackSimulation/Controller_Updated/DDoS_Traffic_Collector.py): Python script to capture and write packets to a .csv file.
        * [My_Switch.py](AttackSimulation/Controller_Updated/My_Switch.py): Python script for simulating switch.
    * [Mininet_Updated](AttackSimulation/Mininet_Updated):
        * [Benign_Traffic_Generator.py](AttackSimulation/Mininet_Updated/Benign_Traffic_Generator.py): Python script to generate normal traffic using iperf.
        * [DDoS_Traffic_Generator.py](AttackSimulation/Mininet_Updated/DDoS_Traffic_Generator.py): Python script to simulate DDoS attacks using hping3.
        * [Topology.py](AttackSimulation/Mininet_Updated/Topology.py): software defined network topology.
* [Data](Data): subdirectory containing all data used for making and evaluating predictions.
    * [SYN.zip](Data/SYN.zip): zip archive of generated traffic, featuring benign transmissions and SYN DDoS attacks.
    * [UDP.zip](Data/UDP.zip): zip archive of generated traffic, featuring benign transmissions and UDP DDoS attacks.
    * [x_test.csv](Data/x_test.csv): preprocessed and normalised data used to test model during training.
    * [x.csv](Data/x.csv): preprocessed and normalised data used to train model.
    * [y_test.csv](Data/y_test.csv): known truths of `x_test.csv`.
    * [y.csv](Data/y.csv): known truths of `x.csv`.
* [Models](Models): subdirectory containing our serialised model and associated files.
    * [random_forest.joblib](Models/random_forest.joblib): Scikit-Learn GridSearchCV serialised with joblib.
    * [std_scaler.joblib](Models/std_scaler.joblib): Scikit-Learn StandardScaler serialised with joblib.
* [Modules](Modules): subdirectory containing any modules we write for use in this project and others.
    * [rf_wrapper.py](Modules/rf_wrapper.py): Python file defining a class that wraps our model (to be used with various projects), as well as a helper function to transform data to match the preprocessing done in training.
* [Predictions](Predictions): subdirectory that predictions are saved to.
    * [SYN_23-05-2024.zip](Predictions/SYN_23-05-2024.zip): zip archive containing a .csv of predictions made on the SYN dataset on the 23rd of April, 2024.
    * [UDP_23-05-2024.zip](Predictions/UDP_23-05-2024.zip): zip archive containing a .csv of predictions made on the UDP dataset on the 23rd of April, 2024.
* [AttackPredictionApp.py](AttackPredictionApp.py): front end GUI application.
* [main.py](main.py): Python file to run project.
* [predict.ipynb](predict.ipynb): Jupyter notebook showing usage of `Modules/rf_wrapper.py` to make predictions on `Data/SYN.zip` and `Data/UDP.zip`.
* [README.md](README.md): this markdown file.
* [requirements.txt](requirements.txt): text file outlining required versions of various Python packages used.
