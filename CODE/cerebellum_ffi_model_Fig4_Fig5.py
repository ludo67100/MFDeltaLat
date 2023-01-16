
'''
Simulation of a Feedforward Inhibitory Network using NEST 2.20

All neurons are modelled as Integrate and fire unit

To mimic Purkinje cell, the LIF neuron is driven with a Poisson type input and 
gamma process whose rate was varied in a sinusoidal fashion

The synapses are modelled as conductance transient 
and have short-term facilitation and short-term-depression (Tsodyka-Markram Synapse)

Stimulus inputs are presented using the device spike_generator. it is connected to the
neuron via Parrot neuron in order to vary the synaptic strengths

Free variables: 
1. Short-term dynamics of synapses A and U for both excitatory and inhibitory synapses
2. Number of stimulus pulse [e..g 1, 2,...] stim_count
3. Interval between stimulus pulses stim_freq
4. Delay between excitation and inhibition arriving at the PC ei_delay

The data will be save in the .dat [membrane potential] and .gdf files [spiking activity]. 
You can load the .gdf file using e.g.
xx = np.loadtxt('file_name.gdf')

and diplay the data as
plt.plot(xx[:,1],xx[:,0],'.') # this will render each trial as a row of dots

You can load the .dat file using e.g.
xx = np.loadtxt('file_name.dat')

and diplay the data as
plt.plot(xx[:,1],xx[:,2],'.') # this will render each trial as a row of dots

@ Arvind Kumar, KTH, Stockholm, Sweden. 2022

'''
import nest
import numpy as np

import os.path

# Parameter ranges for Ae, Ue, Ai, Ui, stim freq, stim count and ei_delay
# STD parameters
Ue = np.array((0.02,0.03,0.05,0.07,0.1,0.2,0.3,0.4))
Ui = np.array((0.03,0.05,0.07,0.1,0.15,0.2,0.3,0.4))

# EI Weights
Ae = np.array((0.5,1.5,2.,2.5,3.,3.5,4.))*1.5
Ai = np.array((1.0,1.5,2.,2.5,3.,3.5,4.,4.5,5.0))*1.

######### Parameters to be varied ###############
stim_freq = [10.,20.,30.,40., 50., 75., 100., 125., 150., 175., 200.]
ei_delay = np.array((-5.,-4.,-3.,-2.,-1.,0.,1.,2.,3.,4.,5.,6.))
stim_count = [1, 2, 3, 4, 5, 6, 7]

######### When you want to run a single case ###############
Ue = [0.03]
Ui = [0.3]
Ae = [2.0]
Ai = [1.5]

stim_freq = [10]
ei_delay = [0.] 
stim_count = [5]

####################### These parameters are fixed for neurons and for synapses
# Intrinsic properties -- capacitance, baseline activity etc.
intrinsic_param = dict({'ei_delay': 1.,'poi_rate':900.,'gamma_rate':2000.,'gamma_freq':157.,'gamma_ac':10.,'Tau_Syn_Inh':5.0,'Cm':250.})
exc_weight = dict({'Tau_psc': 1.5, 'Tau_rec':30.,'Tau_fac': 500., 'U': 0.015, 'A':100.})
inh_weight = dict({'Tau_psc': 1.5, 'Tau_rec':100.,'Tau_fac': 800., 'U': 0.4,  'A':-3.1})
#######################

sim_time = 1200
no_trial = 200 # this will translate to number of neurons -- each neuron is one trial

# Synapses
Je_ext = 1.0/2. # will give 0.2 mV @-55mV

stim_start = 200.

for k1 in range(len(stim_freq)): # frequency
    stim_interval  = np.round((1000./stim_freq[k1])*10.)/10.
    for k2 in range(len(ei_delay)): # EI delay
        for k3 in range(len(stim_count)): # number of spikes
            if stim_count[k3]>0:
                test_spk_time = np.zeros(stim_count[k3])
                for ii in range(stim_count[k3]): # create the spike train
                    test_spk_time[ii] = stim_start+stim_interval*ii
            else:
                test_spk_time = np.zeros(1)
                test_spk_time[0] = 500.
            
            gran_cell_stim = test_spk_time
            interneuron_stim= gran_cell_stim + ei_delay[k2]
            print('Exc:',gran_cell_stim,'Inh:',interneuron_stim)
            
            # Set the base parameters
            ii = 0 # kx+1
            Tau_Syn_Inh = intrinsic_param['Tau_Syn_Inh']
            Cm = intrinsic_param['Cm']
            neuron_params = {'V_th':-55.0, 'V_reset': -70.0, 't_ref': 2.0, 'g_L':13.5,'C_m':Cm, 'E_ex': 0.0, 'E_in': -80.0, 'tau_syn_ex':1.,'tau_syn_in': Tau_Syn_Inh,'E_L' : -70.}

            gamma_rate = intrinsic_param['gamma_rate']
            gamma_freq = intrinsic_param['gamma_freq']
            gamma_ac = intrinsic_param['gamma_ac']
            poi_rate = intrinsic_param['poi_rate']
            
            for a1 in range(len(Ue)):
                for a2 in range(len(Ae)):
                    for a3 in range(len(Ui)):
                        for a4 in range(len(Ai)):
                            # synapses
                            Tau_psc_I = inh_weight['Tau_psc']     # time constant of PSC (= Tau_inact)
                            Tau_rec_I = inh_weight['Tau_rec']   # recovery time
                            Tau_fac_I = inh_weight['Tau_fac']     # facilitation time
                            U_I       = Ui[a3]    # facilitation parameter U
                            A_I       = -Ai[a4]/Ui[a3]   # PSC weight in pA # 1.6640
                            A_I_add   = A_I * 1.5
                            
                            Tau_psc_E = exc_weight['Tau_psc']    # time constant of PSC (= Tau_inact)
                            Tau_rec_E = exc_weight['Tau_rec']   # recovery time
                            Tau_fac_E = exc_weight['Tau_fac']   # facilitation time
                            U_E       = Ue[a1]   # facilitation parameter U
                            A_E       = Ae[a2]/Ue[a1]  # PSC weight in pA -- -0.3420mV
                            # File names to save the mem. traces
                            f_name = 'neuron_' + 'Ue_' + str(a1) + '_' + 'Ae_' + str(a2) + '_' + 'Ui_' + str(a3) + '_' + 'Ai_' + str(a4) + '_freq_' + str(stim_freq[k1]) + '_delay_' + str(ei_delay[k2]) + '_count_' + str(stim_count[k3])
                            #f_name = 'neuron' + '_freq_' + str(stim_freq[k1]) + '_delay_' + str(ei_delay[k2]) + '_count_' + str(stim_count[k3])
                            fx = './data/' +f_name + '-107-0.gdf'

                            if os.path.isfile(fx)==0:
                                nest.ResetKernel()
                                nest.SetStatus([0],{'data_path':'./data','overwrite_files': True})

                                # create neuron and parrots
                                pur = nest.Create('iaf_cond_alpha', no_trial,neuron_params)
                                #set mempot to a random value
                                v1 = np.random.uniform(low=-70.,high=-58.,size=no_trial)
                                vinit = [{'V_m': nid} for nid in v1]
                                nest.SetStatus(pur,vinit)
                                
                                parrot_ex = nest.Create('parrot_neuron',1)
                                parrot_in = nest.Create('parrot_neuron',1)
                                
                                # Spike detectors
                                sd = nest.Create('spike_detector',1)
                                nest.SetStatus(sd,{'label':f_name,'to_file':True,'to_memory':False})

                                # Poisson Generator
                                poi = nest.Create('poisson_generator',1,{'rate':poi_rate})
                                # Gamma generator -- for quasi-periodic inputs
                                gamma_stim = nest.Create('sinusoidal_gamma_generator', n=1,params=[{'rate': gamma_rate, 'amplitude': gamma_ac, 'frequency': gamma_freq, 'phase': 0.0, 'order': 4.0}])

                                # Create spike generators and connect
                                gex = nest.Create('spike_generator', params = {'spike_times': gran_cell_stim.tolist()})
                                gin = nest.Create('spike_generator', params = {'spike_times':interneuron_stim.tolist()})

                                nest.Connect(gex,parrot_ex)
                                nest.Connect(gin,parrot_in)

                                # set synapse parameters:
                                syn_param_exc = {"tau_psc" :  Tau_psc_E,
                                "tau_rec" :  Tau_rec_E,
                                "tau_fac" :  Tau_fac_E,
                                "U"       :  U_E,
                                "delay"   :  0.1,
                                "weight"  :  A_E,
                                "u"       :  0.0,
                                "x"       :  1.0}

                                syn_param_inh = {"tau_psc" :  Tau_psc_I,
                                "tau_rec" :  Tau_rec_I,
                                "tau_fac" :  Tau_fac_I,
                                "U"       :  U_I,
                                "delay"   :  0.1,
                                "weight"  :  A_I,
                                "u"       :  0.0,
                                "x"       :  1.0}

                                syn_param_static = {'weight':Je_ext,'delay':1.0}

                                nest.CopyModel("tsodyks_synapse","syn_exc",syn_param_exc)
                                nest.CopyModel("tsodyks_synapse","syn_inh",syn_param_inh)
                                nest.CopyModel("static_synapse","syn_static",syn_param_static)

                                nest.Connect(parrot_ex, pur, syn_spec={'model':'syn_exc'}) #4.5,1.) # Exc Facil
                                nest.Connect(parrot_in, pur, syn_spec={'model':'syn_inh'}) #4.5,1.) # Inh Dep

                                nest.Connect(gamma_stim,pur,syn_spec={'model':'syn_static'}) # exc static
                                nest.Connect(poi,pur,syn_spec={'model':'syn_static'}) # exc static

                                nest.Connect(pur,sd)
                                # simulate
                                sim_time = interneuron_stim[-1] + 300.
                                conn3 = nest.GetConnections(parrot_in)
                                nest.SetStatus(conn3, {"weight": A_I_add})
                                nest.Simulate(sim_time)
                                
