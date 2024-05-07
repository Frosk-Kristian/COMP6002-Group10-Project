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
* [Data](Data): subdirectory containing all data used for making and evaluating predictions.
    * [x_test.csv](Data/x_test.csv): preprocessed and normalised data used to test model during training.
    * [y_test.csv](Data/y_test.csv): known truths of x_test.csv.
* [Models](Models): subdirectory containing our serialised model and associated files.
    * [random_forest.joblib](Models/random_forest.joblib): 
    * [std_scaler.joblib](Models/std_scaler.joblib): 
* [Modules](Modules): subdirectory containing any modules we write for use in this project and others.
    * [rf_wrapper.py](Modules/rf_wrapper.py): Python file defining a class that wraps our model (to be used with various projects), as well as a helper function to transform data to match the preprocessing done in training.
* [main.py](main.py): Python file to run project.
* [README.md](README.md): this markdown file.
* [requirements.txt](requirements.txt): text file outlining required versions of various Python packages used.
* [test.ipynb](test.ipynb): Jupyter notebook showing example usage of `Modules/rf_wrapper.py`.
