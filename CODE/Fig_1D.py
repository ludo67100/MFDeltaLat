# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 11:27:25 2021

@author: ludovic.spaeth
"""

mainDataDir = 'D:/01_PAPERS/Binda_Spaeth_et_al/000000_Jan_2023/SOURCE_DATA'

#---------------------------------------------------------------------------------------------------
#------------------------The code below will generate the plots as shown in ------------------------
#------------------------------------------the paper------------------------------------------------
#---------------------------------------------------------------------------------------------------

import pandas as pd 
import numpy as np 
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
from matplotlib import pyplot as plt 
import seaborn as sn 

listOfSheets = pd.ExcelFile('{}/MossyFibersSpikeLatencies.xlsx'.format(mainDataDir)).sheet_names

centeredLatencies = []

fig,ax = plt.subplots(1,2)

lab = 1

LatenciesFromStimOnset = []

for sheet,color,marker in zip(listOfSheets,['red','blue','green','purple','orange'], ['o','D','s','v','^']):
    
    df = pd.read_excel('{}/MossyFibersSpikeLatencies.xlsx'.format(mainDataDir),header=0,index_col=0, sheet_name=sheet)
    
    
    firstStimLatencies = df['Stim#1']
    
    centeredLat = df['Stim#1']-df['Stim#1'].mean()
    centeredLatencies.append(centeredLat.values)
    ax[1].hist(np.ravel(centeredLat), bins=np.arange(-0.15, 0.15, 0.01), color=color, alpha=0.5)
    
    sn.swarmplot(data=firstStimLatencies,ax=ax[0],color=color,alpha=0.2,zorder=0)
    ax[0].scatter(0,firstStimLatencies.mean(),marker=marker,color=color,zorder=1,s=40,label='Rosette_{}'.format(lab))
    ax[0].errorbar(0,firstStimLatencies.mean(),yerr=firstStimLatencies.std(),color=color)
    
    LatenciesFromStimOnset.append(firstStimLatencies.mean())
    
    lab += 1 
    
ax[0].legend(loc='best')
ax[0].set_ylabel('First spike latency \nfrom stim onset [ms]')

ax[0].set_title('Avg. Lat = {} +/- {} ms'.format(round(np.nanmean(LatenciesFromStimOnset),2),
                                                 round(np.nanstd(LatenciesFromStimOnset),2)))



finalCenteredLat = []

for i in (centeredLatencies):
    for j in i:
        finalCenteredLat.append(j)
        
avgJitter = np.nanmean(np.abs(finalCenteredLat))
JitterSD = np.nanstd(finalCenteredLat)

ax[1].set_title('Avg. Jitter = {} +/- {} ms'.format(round(avgJitter,3),round(JitterSD,2)))
ax[1].set_xlabel('Jitter [ms]')
ax[1].set_ylabel('Count')


