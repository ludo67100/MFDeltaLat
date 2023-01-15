# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 14:33:51 2022

Do histograms + correlations from Surface and Single_Protocol_ProcessedData.xlsx

@author: ludovicspaeth
"""

mainDataDir = 'D:/01_PAPERS/Binda_Spaeth_et_al/000000_Jan_2023/SOURCE_DATA'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

import matplotlib.pyplot as plt 
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams.update({'font.size': 7})
import pandas as pd 
import numpy as np
import seaborn as sn 
from scipy import stats as st
import electroPyy


singleDataFile = '{}/Single_Protocol_ProcessedData.xlsx'.format(mainDataDir)
surfaceDataFile = '{}/Surface_Protocol_ProcessedData.xlsx'.format(mainDataDir)


singleData = pd.read_excel(singleDataFile, header=0, index_col=0)
surfaceData = pd.read_excel(surfaceDataFile, header=0, index_col=0)

fig, ax = plt.subplots(1, singleData.shape[1], figsize=(18,2))
fig.suptitle('Single vs Surface')


for feature, idx in zip(singleData.columns.values, range(len(singleData.columns.values))): 
    
    single = singleData[feature].values
    surface = surfaceData[feature].values
    
    
    mergedBins = np.linspace(min(list(single)+list(surface)), max(list(single)+list(surface)), 20)
    
    #Histogram
    ax[idx].hist(single, bins=mergedBins, color='orange', alpha=0.3, density=True)
    ax[idx].hist(surface, bins=mergedBins, color='0.5', alpha=0.3, density=True)
    
    #KDE curve on top
    sn.kdeplot(single,  color='orange', ax=ax[idx])
    sn.kdeplot(surface,  color='0.5', ax=ax[idx])
    
    
    ax[idx].set_xlabel(feature)
    
    #Do stats
    print()
    print('----------------------------------------------')
    print('Single vs Surface: {}'.format(feature))
    print('    single (avg +/- SD): {:.2f} +/- {:.2f}    n={}'.format(np.nanmean(single), np.nanstd(single), len(single)))
    print('    surface (avg +/- SD): {:.2f} +/- {:.2f}    n={}'.format(np.nanmean(surface), np.nanstd(surface), len(surface)))
    
    #Do shapiro-wilk, then leveve, and t-test if both pass. Otherwise, do MWU
    shapiroResults = [st.shapiro(x).pvalue for x in [single, surface]]
    
    if shapiroResults[0] < 0.05 or shapiroResults[1] < 0.05: 
        print('     Shapiro-Wilk H0 is rejected, at least one distribution is not normal')
        
        mwu = st.mannwhitneyu(single, surface)
        print('     MannWhitneyU test stat = {:.3f} | p-value = {}'.format(mwu[0], mwu[1]))
        ax[idx].set_title('p={}'.format(mwu[1]))
        
    else: 
        print('     Shapiro-Wilk H0 cannot be rejected, both distributions are normal')
        
        leveneResults = [st.levene(x).pvalue for x in [single, surface]]
        
        if leveneResults[0] < 0.05 or shapiroResults[1] < 0.05: 
            
            print('      Levene H0 is rejected, the 2 distributions do not have equal variance')
            
            ttest = st.ttest_ind(single, surface, equal_var=False)
            print('      Welch test stat = {:.3f} | p-value = {}'.format(ttest[0], ttest[1]))
            ax[idx].set_title('p={}'.format(ttest[1]))
            
        else: 
            
            print('      Levene H0 cannot be rejected, the 2 distributions have equal variance')
            
            ttest = st.ttest_ind(single, surface, equal_var=True)
            print('      Ind. T-test stat = {:.3f} | p-value = {}'.format(ttest[0], ttest[1]))
            ax[idx].set_title('p={}'.format(ttest[1]))
        
        
    
    
    
fig.tight_layout()

#--------------------------------------------------------------------------------------------------------------

groups = [1,0]
groupLabels = ['FFI', 'beyond FFI']

for group, grouplabel in zip(groups, groupLabels): 
    
    print()
    print()
    print('#####' + grouplabel + '#####')
    
    fig, ax = plt.subplot_mosaic(layout=
                                 [
                                     ['Both', 'Single'],
                                     ['Both', 'Surface'],
                                     ], 
                                 figsize=(5,4)
                                 )
    
    ax['Single'].set_title('Single')
    ax['Surface'].set_title('Surface')
    ax['Both'].set_title('Single + Surface')
    
    fig.suptitle('Linear fit - Single & Surface data in {}'.format(grouplabel))

    
    if group == 0 or group == 1:
        single = [abs(singleData.loc[singleData['Group']==group]['EPSQ_pC'].values), abs(singleData.loc[singleData['Group']==group]['IPSQ_pC'].values)]
        surface = [abs(surfaceData.loc[surfaceData['Group']==group]['EPSQ_pC'].values), abs(surfaceData.loc[surfaceData['Group']==group]['IPSQ_pC'].values)]
        
        #First the single data
        print('    Single Data ------------')
        ax['Single'].scatter(single[0], single[1], color='tab:orange')
        ax['Single'].set_xlabel('EPSQs (pC)'); ax['Single'].set_ylabel('IPSQs (pC)')
        ax['Both'].scatter(single[0], single[1], color='tab:orange')
        px, nom, lpb, upb, r2, std, coeffs = electroPyy.core.Regression.LinReg(single[0],single[1],
                                                                       conf=0.95,printparams=True,
                                                                       plot=False) 
        
        #Do stats
        print(st.linregress(single[0],single[1]))
        print('n={}'.format(len(single[0])))
        
        ax['Single'].plot(px, nom, color='tab:orange', ls='--')
        ax['Both'].plot(px, nom, color='tab:orange', ls='--')
        ax['Single'].fill_between(px, nom+std, nom-std, color='tab:orange', alpha=0.2)
        ax['Both'].fill_between(px, nom+std, nom-std, color='tab:orange', alpha=0.2)
        
        print('    Surface Data ------------')
        ax['Surface'].scatter(surface[0], surface[1], color='0.5')
        ax['Surface'].set_xlabel('EPSQs (pC)'); ax['Surface'].set_ylabel('IPSQs (pC)')
        ax['Both'].scatter(surface[0], surface[1], color='0.5')
        ax['Both'].set_xlabel('EPSQs (pC)'); ax['Both'].set_ylabel('IPSQs (pC)')

        px, nom, lpb, upb, r2, std, coeffs = electroPyy.core.Regression.LinReg(surface[0],surface[1],
                                                                       conf=0.95,printparams=True,
                                                                       plot=False) 
        
        #Do stats
        print(st.linregress(surface[0],surface[1]))
        print('n={}'.format(len(surface[0])))
        
        #Then surface data
        ax['Surface'].plot(px, nom, color='0.5', ls='--')
        ax['Both'].plot(px, nom, color='0.5', ls='--')
        ax['Surface'].fill_between(px, nom+std, nom-std, color='0.5', alpha=0.2)
        ax['Both'].fill_between(px, nom+std, nom-std, color='0.5', alpha=0.2)
        
        #Now merge the two
        print('   Surface + single data ------------')
        px, nom, lpb, upb, r2, std, coeffs = electroPyy.core.Regression.LinReg(np.concatenate((single[0],surface[0])),
                                                                               np.concatenate((single[1],surface[1])),
                                                                               conf=0.95,printparams=True,
                                                                               plot=False) 
        
        #Do stats
        print(st.linregress(np.concatenate((single[0],surface[0])),np.concatenate((single[1],surface[1]))))
        print('n={}'.format(len(np.concatenate((single[0],surface[0])))))
        
        ax['Both'].plot(px, nom, color='black', ls='--')
        ax['Both'].fill_between(px, nom+std, nom-std, color='black', alpha=0.2)
        

    fig.tight_layout()
    
#Merge both groups--------------------------------------------------------------------------------------------------------

print()
print('#####' + 'Merged Groups' + '#####')

fig, ax = plt.subplot_mosaic(layout=
                             [
                                 ['Both', 'Single'],
                                 ['Both', 'Surface'],
                                 ], 
                             figsize=(5,4)
                             )

ax['Single'].set_title('Single')
ax['Surface'].set_title('Surface')
ax['Both'].set_title('Single + Surface')

fig.suptitle('Linear fit - Single & Surface data')

single = [abs(singleData['EPSQ_pC'].values), abs(singleData['IPSQ_pC'].values)]
surface = [abs(surfaceData['EPSQ_pC'].values), abs(surfaceData['IPSQ_pC'].values)]


#First the single data
print('    Single Data ------------')
ax['Single'].scatter(single[0], single[1], color='tab:orange')
ax['Single'].set_xlabel('EPSQs (pC)'); ax['Single'].set_ylabel('IPSQs (pC)')
ax['Both'].scatter(single[0], single[1], color='tab:orange')
px, nom, lpb, upb, r2, std, coeffs = electroPyy.core.Regression.LinReg(single[0],single[1],
                                                               conf=0.95,printparams=True,
                                                               plot=False) 

#Do stats
print(st.linregress(single[0],single[1]))
print('n={}'.format(len(single[0])))

ax['Single'].plot(px, nom, color='tab:orange', ls='--')
ax['Single'].fill_between(px, nom+std, nom-std, color='tab:orange', alpha=0.2)
ax['Both'].plot(px, nom, color='tab:orange', ls='--')
ax['Both'].fill_between(px, nom+std, nom-std, color='tab:orange', alpha=0.2)

print('    Surface Data ------------')
ax['Surface'].scatter(surface[0], surface[1], color='0.5')
ax['Surface'].set_xlabel('EPSQs (pC)'); ax['Surface'].set_ylabel('IPSQs (pC)')
ax['Both'].scatter(surface[0], surface[1], color='0.5')
ax['Both'].set_xlabel('EPSQs (pC)'); ax['Both'].set_ylabel('IPSQs (pC)')

px, nom, lpb, upb, r2, std, coeffs = electroPyy.core.Regression.LinReg(surface[0],surface[1],
                                                               conf=0.95,printparams=True,
                                                               plot=False) 

#Do stats
print(st.linregress(surface[0],surface[1]))
print('n={}'.format(len(surface[0])))

#Then surface data
ax['Surface'].plot(px, nom, color='0.5', ls='--')
ax['Surface'].fill_between(px, nom+std, nom-std, color='0.5', alpha=0.2)
ax['Both'].plot(px, nom, color='0.5', ls='--')
ax['Both'].fill_between(px, nom+std, nom-std, color='0.5', alpha=0.2)

#Now merge the two
print('   Surface + single data ------------')
px, nom, lpb, upb, r2, std, coeffs = electroPyy.core.Regression.LinReg(np.concatenate((single[0],surface[0])),
                                                                       np.concatenate((single[1],surface[1])),
                                                                       conf=0.95,printparams=True,
                                                                       plot=False) 

#Do stats
print(st.linregress(np.concatenate((single[0],surface[0])),np.concatenate((single[1],surface[1]))))

print('n={}'.format(len(np.concatenate((single[0],surface[0])))))

ax['Both'].plot(px, nom, color='black', ls='--')
ax['Both'].fill_between(px, nom+std, nom-std, color='black', alpha=0.2)


fig.tight_layout()
        
        
        
        


        
        
        
        

