# MFDeltaLat

This repository gathers scripts that were used to analyse the data presented in Effect of excitation and inhibition delay in a 
feedforward inhibitory pathway on mice cerebellar Purkinje cell output (F. Binda, L. Spaeth, A. Kumar and P.Isope)


## HOW TO USE WITH SPYDER
These scripts were written in Python 3.9 and executed in Spyder 5 (Anaconda is recommended: https://www.anaconda.com/products/distribution)

You'll need the following modules: Pandas, numpy, matplotlib, seaborn, scipy and electroPyy

### 1. Install common modules
```pip install pandas, numpy, matplotlib, seaborn, scipy``` 

### 2. Install electroPyy
install ```git``` (choose correponding version for Windows, MacOS or Linux) : https://git-scm.com/downloads
install electroPyy via clone from GitHub
```
pip install git+https://github.com/ludo67100/electroPyy.git
``` 

### 3. Download data
Download and unzip SOURCE_DATA.zip anywhere on your machine

### 4. Run the scripts in Spyder
Simply copy/paste of open scripts file (.py) in Spyder and set *** mainDataDir *** path with the location of SOURCE_DATA folder in your machine. 

### 5. To run the NEST simulation 
create an environnement and install NEST
```conda create --name ENVNAME -c conda-forge nest-simulator```

