# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 19:06:28 2022

@author: ludovicspaeth
"""

import matplotlib.pyplot as plt 
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams.update({'font.size': 7})

fig, ax = plt.subplots(1,2)

#single 
labels = ['Group 1', 'Group 2 E first', 'Group 2 I first', 'Group 3']
proportions = [29,6,10,4]

ax[0].pie(proportions, labels=labels, autopct='%1.1f%%', startangle=90)
ax[0].set_title('Single stim.')

#surface 
proportions = [20,24,10,10]
ax[1].pie(proportions, labels=labels, autopct='%1.1f%%', startangle=90)
ax[1].set_title('Surface stim.')