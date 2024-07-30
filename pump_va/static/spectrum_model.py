import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.signal import windows
from datetime import datetime,timedelta
import random

class pump_equipment:
    def __init__(self):
        self.rpm=1160
        self.no_of_vanes = 8
        self.original_sampling_rate = 42000
        self.no_of_bearing_elements = 8
        self.ball_pass_frequency_outer=0.4*self.no_of_bearing_elements*self.rpm
        self.ball_pass_frequency_inner=0.6*self.no_of_bearing_elements*self.rpm
        self.fundamental_train_frequency=0.4*self.rpm
        self.ball_spin_frequency=0
        self.required_sampling_rate = 21000
        self.vane_pass_frequency =self.no_of_vanes*self.rpm
        self.original_duration=10
        self.required_duration=1
        self.no_of_random_waves = 100
        self.random_wave_amp_ul = 0.01
        self.random_wave_freq_ul = 1000
        
        
    def convert_to_frequency_domain(self, data, sampling_rate):    
        window = windows.hann(len(data))
        windowed_data = data * window
        n = len(windowed_data)
        fft_amplitude = fft(windowed_data)
        frequencies = np.fft.fftfreq(n, d=1/sampling_rate)
        fft_amplitude = np.abs(fft_amplitude[:n // 2]) * 2 / n
        frequencies = frequencies[:n // 2]
        return frequencies, fft_amplitude
    
    def create_wave(self,amplitude,frequency,time_array,phase_shift=0):
        wave_accelaration = amplitude*np.sin(2*np.pi*frequency*time_array+phase_shift)
        return wave_accelaration
    
    def generate_random_data(self,duration,sampling_rate,no_of_waves,amp_ul,freq_ul,amp_ll=0,freq_ll=0):
        no_of_samples = int(sampling_rate*duration)
        time_array =np.linspace(0,duration,no_of_samples,endpoint=False)
        cummulative_wave = np.zeros(no_of_samples)
        for i in range(no_of_waves):
            amplitude = random.uniform(amp_ll,amp_ul)
            frequency = random.uniform(freq_ll,freq_ul)
            wave = self.create_wave(amplitude,frequency,time_array)
            cummulative_wave += wave
        all_axes_random_waves = np.column_stack((cummulative_wave,cummulative_wave,cummulative_wave)) 
        return all_axes_random_waves
    
    
    def generate_random_cavitation_data(self, duration, sampling_rate, no_of_waves, amp_ul, freq_ul, amp_ll=0, freq_ll=0):
        no_of_samples = int(sampling_rate * duration)
        time_array = np.linspace(0, duration, no_of_samples, endpoint=False)
        cummulative_wave = np.zeros(no_of_samples)
        cummulative_wave2 = np.zeros(no_of_samples)
        cummulative_wave3 = np.zeros(no_of_samples)
        for i in range(no_of_waves):
            frequency = random.uniform(freq_ll, freq_ul)
            mean_frequency = (freq_ll + freq_ul) / 2
            std_dev = (freq_ul - freq_ll) / 6  
            amplitude = amp_ul * np.exp(-((frequency - mean_frequency) ** 2) / (2 * std_dev ** 2))
            
            wave = self.create_wave(amplitude, frequency, time_array)
            cummulative_wave += wave
            
        for i in range(no_of_waves):
            frequency = random.uniform(freq_ll, freq_ul)
            mean_frequency = (freq_ll + freq_ul) / 2
            std_dev = (freq_ul - freq_ll) / 6  
            amplitude = amp_ul * np.exp(-((frequency - mean_frequency) ** 2) / (2 * std_dev ** 2))
            
            wave = self.create_wave(amplitude, frequency, time_array)
            cummulative_wave2 += wave
            
        for i in range(no_of_waves):
            frequency = random.uniform(freq_ll, freq_ul)
            mean_frequency = (freq_ll + freq_ul) / 2
            std_dev = (freq_ul - freq_ll) / 6 
            amplitude = amp_ul * np.exp(-((frequency - mean_frequency) ** 2) / (2 * std_dev ** 2))
            
            wave = self.create_wave(amplitude, frequency, time_array)
            cummulative_wave3 += wave
        
        all_axes_random_waves = np.column_stack((cummulative_wave, cummulative_wave2*0.08, cummulative_wave3*0.05))
        return all_axes_random_waves
    
    def resample_data(self,original_data,original_duration,required_duration,original_sampling_rate,required_sampling_rate):
        if(original_duration>=required_duration):
            data = original_data.values[:original_sampling_rate*required_duration,:]
        if(original_sampling_rate>=required_sampling_rate):
            downsampling_factor = (int)(original_sampling_rate/required_sampling_rate)
            resampled_data = data[::downsampling_factor]
        elif(original_sampling_rate<required_sampling_rate):
            num_original_samples = len(data)
            num_target_samples = int(required_duration * required_sampling_rate)
            original_time = np.linspace(0, required_duration, num=num_original_samples, endpoint=False)
            target_time = np.linspace(0, required_duration, num=num_target_samples, endpoint=False)
            resampled_data = np.interp(target_time, original_time, data)
        return resampled_data
    
    def get_time_stamps(self, sampling_rate, duration):
        num_samples = int(sampling_rate * duration)
        timestamps = np.linspace(0, duration, num_samples, endpoint=False)
        vibration_time = pd.DataFrame({'time': timestamps})
        reference_time = datetime.now()
        vibration_time['datetime'] = vibration_time['time'].apply(lambda x: reference_time + timedelta(seconds=x))
        vibration_time['time_str'] = vibration_time['datetime'].dt.strftime('%H:%M:%S.%f')
        vibration_time['time_str'] = vibration_time['time_str'].astype(str)


        return (
            vibration_time['time_str'].values.astype(str).tolist(),
            vibration_time['time_str'].values.astype(str).tolist(),
            vibration_time['time_str'].values.astype(str).tolist()
        )
    
    def get_freq_domain_data(self,data,sampling_rate):
        ts_amp_x = data[:,0].astype(float)
        fft_freq_x,fft_amp_x= self.convert_to_frequency_domain(ts_amp_x, sampling_rate)
        ts_amp_y = data[:,1].astype(float)
        fft_freq_y,fft_amp_y= self.convert_to_frequency_domain(ts_amp_y, sampling_rate)
        ts_amp_z = data[:,2].astype(float)
        fft_freq_z,fft_amp_z= self.convert_to_frequency_domain(ts_amp_z, sampling_rate)       
        return fft_freq_x,fft_amp_x,fft_freq_y,fft_amp_y,fft_freq_z,fft_amp_z,ts_amp_x,ts_amp_y,ts_amp_z
        
    def generate_peak_data(self,data,sampling_rate,duration,amp_x,freq_x,amp_y,freq_y,amp_z,freq_z,x_phase_shift=0,y_phase_shift=0,z_phase_shift=0):
        time_array = np.linspace(0,duration,int(sampling_rate*duration),endpoint=False)        
        x_unbalance_wave_form = self.create_wave(amp_x,freq_x,time_array,x_phase_shift)     
        y_unbalance_wave_form = self.create_wave(amp_y,freq_y,time_array,y_phase_shift)
        z_unbalance_wave_form = self.create_wave(amp_z,freq_z,time_array,z_phase_shift)
        peak_data = np.column_stack((x_unbalance_wave_form,y_unbalance_wave_form,z_unbalance_wave_form))
        updated_data = data+peak_data
        return updated_data   
    

    def generate_normal_data(self,data):
        random_data_set = self.generate_random_data(self.required_duration,self.required_sampling_rate,self.no_of_random_waves,self.random_wave_amp_ul,self.random_wave_freq_ul)
        vibration_normal_equipment = data+random_data_set
        return vibration_normal_equipment   
    
    def generate_unbalance_data(self,data,sampling_rate,duration,amp_1x,freq_1x,amp_1y,freq_1y,amp_1z,freq_1z):
        unbalance_fault_data_1x = self.generate_peak_data(data,sampling_rate,duration,amp_1x,freq_1x,amp_1y,freq_1y,amp_1z,freq_1z)
        updated_data = data+unbalance_fault_data_1x
        return updated_data
    
    def generate_misalignment_data(self,data,sampling_rate,duration,amp_1x,freq_1x,amp_1y,freq_1y,amp_1z,freq_1z,amp_2x,freq_2x,amp_2y,freq_2y,amp_2z,freq_2z,amp_3x,freq_3x,amp_3y,freq_3y,amp_3z,freq_3z):
        misalignment_fault_data_1x = self.generate_peak_data(data,sampling_rate,duration,amp_1x,freq_1x,amp_1y,freq_1y,amp_1z,freq_1z)
        misalignment_fault_data_2x = self.generate_peak_data(data,sampling_rate,duration,amp_2x,freq_2x,amp_2y,freq_2y,amp_2z,freq_2z)
        misalignment_fault_data_3x = self.generate_peak_data(data,sampling_rate,duration,amp_3x,freq_3x,amp_3y,freq_3y,amp_3z,freq_3z)
        updated_data = data+misalignment_fault_data_1x+misalignment_fault_data_2x+misalignment_fault_data_3x
        return updated_data
    
    def generate_outerracefault_data(self,data,sampling_rate,duration,amp_1x,freq_1x,amp_1y,freq_1y,amp_1z,freq_1z,amp_2x,freq_2x,amp_2y,freq_2y,amp_2z,freq_2z,amp_3x,freq_3x,amp_3y,freq_3y,amp_3z,freq_3z,amp_4x,freq_4x,amp_4y,freq_4y,amp_4z,freq_4z,amp_5x,freq_5x,amp_5y,freq_5y,amp_5z,freq_5z):
        outerrace_fault_bpfo1x = self.generate_peak_data(data,sampling_rate,duration,amp_1x,freq_1x,amp_1y,freq_1y,amp_1z,freq_1z)
        outerrace_fault_bpfo2x = self.generate_peak_data(data,sampling_rate,duration,amp_2x,freq_2x,amp_2y,freq_2y,amp_2z,freq_2z)
        outerrace_fault_bpfo3x = self.generate_peak_data(data,sampling_rate,duration,amp_3x,freq_3x,amp_3y,freq_3y,amp_3z,freq_3z)
        outerrace_fault_bpfo4x = self.generate_peak_data(data,sampling_rate,duration,amp_4x,freq_4x,amp_4y,freq_4y,amp_4z,freq_4z)
        outerrace_fault_bpfo5x = self.generate_peak_data(data,sampling_rate,duration,amp_5x,freq_5x,amp_5y,freq_5y,amp_5z,freq_5z)
        updated_data = data+outerrace_fault_bpfo1x+outerrace_fault_bpfo5x+outerrace_fault_bpfo2x+outerrace_fault_bpfo3x+outerrace_fault_bpfo4x
        return updated_data
    
    def generate_innerracefault_data(self, data, sampling_rate, duration, amp_1x, freq_1x, amp_1y, freq_1y, amp_1z, freq_1z,
                                    amp_2x, freq_2x, amp_2y, freq_2y, amp_2z, freq_2z,
                                    amp_3x, freq_3x, amp_3y, freq_3y, amp_3z, freq_3z,
                                    amp_4x, freq_4x, amp_4y, freq_4y, amp_4z, freq_4z,
                                    amp_5x, freq_5x, amp_5y, freq_5y, amp_5z, freq_5z):
        innerrace_fault_bpfi1x = self.generate_peak_data(data, sampling_rate, duration, amp_1x, freq_1x, amp_1y, freq_1y, amp_1z, freq_1z)
        innerrace_fault_bpfi2x = self.generate_peak_data(data, sampling_rate, duration, amp_2x, freq_2x, amp_2y, freq_2y, amp_2z, freq_2z)
        innerrace_fault_bpfi3x = self.generate_peak_data(data, sampling_rate, duration, amp_3x, freq_3x, amp_3y, freq_3y, amp_3z, freq_3z)
        innerrace_fault_bpfi4x = self.generate_peak_data(data, sampling_rate, duration, amp_4x, freq_4x, amp_4y, freq_4y, amp_4z, freq_4z)
        innerrace_fault_bpfi5x = self.generate_peak_data(data, sampling_rate, duration, amp_5x, freq_5x, amp_5y, freq_5y, amp_5z, freq_5z)
        updated_data = data + innerrace_fault_bpfi1x + innerrace_fault_bpfi5x + innerrace_fault_bpfi2x + innerrace_fault_bpfi3x + innerrace_fault_bpfi4x
        return updated_data

    
    def generate_cagefault_data(self, data, sampling_rate, duration, amp_1x, freq_1x, amp_1y, freq_1y, amp_1z, freq_1z,
                            amp_2x, freq_2x, amp_2y, freq_2y, amp_2z, freq_2z,
                            amp_3x, freq_3x, amp_3y, freq_3y, amp_3z, freq_3z,
                            amp_4x, freq_4x, amp_4y, freq_4y, amp_4z, freq_4z,
                            amp_5x, freq_5x, amp_5y, freq_5y, amp_5z, freq_5z):
        cagefault_ftf1x = self.generate_peak_data(data, sampling_rate, duration, amp_1x, freq_1x, amp_1y, freq_1y, amp_1z, freq_1z)
        cagefault_ftf2x = self.generate_peak_data(data, sampling_rate, duration, amp_2x, freq_2x, amp_2y, freq_2y, amp_2z, freq_2z)
        cagefault_ftf3x = self.generate_peak_data(data, sampling_rate, duration, amp_3x, freq_3x, amp_3y, freq_3y, amp_3z, freq_3z)
        cagefault_ftf4x = self.generate_peak_data(data, sampling_rate, duration, amp_4x, freq_4x, amp_4y, freq_4y, amp_4z, freq_4z)
        cagefault_ftf5x = self.generate_peak_data(data, sampling_rate, duration, amp_5x, freq_5x, amp_5y, freq_5y, amp_5z, freq_5z)
        updated_data = data + cagefault_ftf1x + cagefault_ftf5x + cagefault_ftf2x + cagefault_ftf3x + cagefault_ftf4x
        return updated_data
    
    def generate_bearing_element_fault_data(self, data, sampling_rate, duration, amp_1x, freq_1x, amp_1y, freq_1y, amp_1z, freq_1z,
                                        amp_2x, freq_2x, amp_2y, freq_2y, amp_2z, freq_2z,
                                        amp_3x, freq_3x, amp_3y, freq_3y, amp_3z, freq_3z,
                                        amp_4x, freq_4x, amp_4y, freq_4y, amp_4z, freq_4z,
                                        amp_5x, freq_5x, amp_5y, freq_5y, amp_5z, freq_5z):
        bearing_element_fault_bsf1x = self.generate_peak_data(data, sampling_rate, duration, amp_1x, freq_1x, amp_1y, freq_1y, amp_1z, freq_1z)
        bearing_element_fault_bsf2x = self.generate_peak_data(data, sampling_rate, duration, amp_2x, freq_2x, amp_2y, freq_2y, amp_2z, freq_2z)
        bearing_element_fault_bsf3x = self.generate_peak_data(data, sampling_rate, duration, amp_3x, freq_3x, amp_3y, freq_3y, amp_3z, freq_3z)
        bearing_element_fault_bsf4x = self.generate_peak_data(data, sampling_rate, duration, amp_4x, freq_4x, amp_4y, freq_4y, amp_4z, freq_4z)
        bearing_element_fault_bsf5x = self.generate_peak_data(data, sampling_rate, duration, amp_5x, freq_5x, amp_5y, freq_5y, amp_5z, freq_5z)
        updated_data = data + bearing_element_fault_bsf1x + bearing_element_fault_bsf5x + bearing_element_fault_bsf2x + bearing_element_fault_bsf3x + bearing_element_fault_bsf4x
        return updated_data
    
    def generate_starvation_fault_data(self, data, sampling_rate, duration, amp_1x, freq_1x, amp_1y, freq_1y, amp_1z, freq_1z,
                                        amp_2x, freq_2x, amp_2y, freq_2y, amp_2z, freq_2z):
        starvation_1x = self.generate_peak_data(data, sampling_rate, duration, amp_1x, freq_1x, amp_1y, freq_1y, amp_1z, freq_1z)
        starvation_vpf1x = self.generate_peak_data(data, sampling_rate, duration, amp_2x, freq_2x, amp_2y, freq_2y, amp_2z, freq_2z)
        updated_data = data+starvation_1x+starvation_vpf1x
        return updated_data
    
    def generate_eccentricity_data(self,data,sampling_rate,duration,amp_1x,freq_1x,amp_1y,freq_1y,amp_1z,freq_1z):
        eccentricity_fault_data_1x = self.generate_peak_data(data,sampling_rate,duration,amp_1x,freq_1x,amp_1y,freq_1y,amp_1z,freq_1z,0,90,0)
        updated_data = data+eccentricity_fault_data_1x
        return updated_data
    
    def generate_bent_shaft_fault_data(self, data, sampling_rate, duration, amp_1x, freq_1x, amp_1y, freq_1y, amp_1z, freq_1z,
                                        amp_2x, freq_2x, amp_2y, freq_2y, amp_2z, freq_2z):
        bent_fault_data_1x = self.generate_peak_data(data, sampling_rate, duration, amp_1x, freq_1x, amp_1y, freq_1y, amp_1z, freq_1z,0,0,180)
        bent_fault_data_2x = self.generate_peak_data(data, sampling_rate, duration, amp_2x, freq_2x, amp_2y, freq_2y, amp_2z, freq_2z,0,0,180)
        updated_data = data+bent_fault_data_1x+bent_fault_data_2x
        return updated_data
    
    def generate_broken_impeller_fault_data(self, data, sampling_rate, duration, amp_1x, freq_1x, amp_1y, freq_1y, amp_1z, freq_1z,
                                            amp_2x, freq_2x, amp_2y, freq_2y, amp_2z, freq_2z,
                                            amp_3x, freq_3x, amp_3y, freq_3y, amp_3z, freq_3z):
        broken_impeller_vpf1x = self.generate_peak_data(data, sampling_rate, duration, amp_1x, freq_1x, amp_1y, freq_1y, amp_1z, freq_1z)
        broken_impeller_vpf_leftsideband_1x = self.generate_peak_data(data, sampling_rate, duration, amp_2x, freq_2x, amp_2y, freq_2y, amp_2z, freq_2z)
        broken_impeller_vpf_rightsideband_1x = self.generate_peak_data(data, sampling_rate, duration, amp_3x, freq_3x, amp_3y, freq_3y, amp_3z, freq_3z)
        updated_data = data+ broken_impeller_vpf1x+broken_impeller_vpf_leftsideband_1x+broken_impeller_vpf_rightsideband_1x
        return updated_data
    
    def generate_cavitation_fault_data(self,data,sampling_rate,duration,no_of_waves,amp_ul,freq_ul,amp_ll,freq_ll):
        noise_data = self.generate_random_cavitation_data(duration,sampling_rate,no_of_waves,amp_ul,freq_ul,amp_ll,freq_ll)
        updated_data = data+noise_data
        return updated_data
    
    def get_frequency_domain_data(self,equipment_condition):
        amp_1x,amp_2x,amp_3x,amp_4x,amp_5x=6,5.74,5.56,5.12,4.7
        freq_1x,freq_2x,freq_3x,freq_4x,freq_5x=self.rpm,self.rpm*2,self.rpm*3,self.rpm*4,self.rpm*5
        amp_1y,amp_2y,amp_3y,amp_4y,amp_5y=0.67,0.61,0.52,0.48,0.43
        freq_1y,freq_2y,freq_3y,freq_4y,freq_5y=self.rpm,self.rpm*2,self.rpm*3,self.rpm*4,self.rpm*5
        amp_1z,amp_2z,amp_3z,amp_4z,amp_5z=0.42,0.37,0.33,0.26,0.22
        freq_1z,freq_2z,freq_3z,freq_4z,freq_5z=self.rpm,self.rpm*2,self.rpm*3,self.rpm*4,self.rpm*5
        ir_freq_1x,ir_freq_2x,ir_freq_3x,ir_freq_4x,ir_freq_5x=self.ball_pass_frequency_inner,self.ball_pass_frequency_inner*2,self.ball_pass_frequency_inner*3,self.ball_pass_frequency_inner*4,self.ball_pass_frequency_inner*5
        ir_freq_1y,ir_freq_2y,ir_freq_3y,ir_freq_4y,ir_freq_5y=self.ball_pass_frequency_inner,self.ball_pass_frequency_inner*2,self.ball_pass_frequency_inner*3,self.ball_pass_frequency_inner*4,self.ball_pass_frequency_inner*5
        ir_freq_1z,ir_freq_2z,ir_freq_3z,ir_freq_4z,ir_freq_5z=self.ball_pass_frequency_inner,self.ball_pass_frequency_inner*2,self.ball_pass_frequency_inner*3,self.ball_pass_frequency_inner*4,self.ball_pass_frequency_inner*5
        or_freq_1x, or_freq_2x, or_freq_3x, or_freq_4x, or_freq_5x = self.ball_pass_frequency_outer*1,self.ball_pass_frequency_outer*2,self.ball_pass_frequency_outer*3,self.ball_pass_frequency_outer*4,self.ball_pass_frequency_outer*5
        or_freq_1y, or_freq_2y, or_freq_3y, or_freq_4y, or_freq_5y = self.ball_pass_frequency_outer*1,self.ball_pass_frequency_outer*2,self.ball_pass_frequency_outer*3,self.ball_pass_frequency_outer*4,self.ball_pass_frequency_outer*5
        or_freq_1z, or_freq_2z, or_freq_3z, or_freq_4z, or_freq_5z = self.ball_pass_frequency_outer*1,self.ball_pass_frequency_outer*2,self.ball_pass_frequency_outer*3,self.ball_pass_frequency_outer*4,self.ball_pass_frequency_outer*5
        bsf_freq_1x, bsf_freq_2x, bsf_freq_3x, bsf_freq_4x, bsf_freq_5x = self.ball_spin_frequency,self.ball_spin_frequency*2,self.ball_spin_frequency*3,self.ball_spin_frequency*4,self.ball_spin_frequency*5
        bsf_freq_1y, bsf_freq_2y, bsf_freq_3y, bsf_freq_4y, bsf_freq_5y = self.ball_spin_frequency,self.ball_spin_frequency*2,self.ball_spin_frequency*3,self.ball_spin_frequency*4,self.ball_spin_frequency*5
        bsf_freq_1z, bsf_freq_2z, bsf_freq_3z, bsf_freq_4z, bsf_freq_5z = self.ball_spin_frequency,self.ball_spin_frequency*2,self.ball_spin_frequency*3,self.ball_spin_frequency*4,self.ball_spin_frequency*5
        ftf_freq_1x, ftf_freq_2x, ftf_freq_3x, ftf_freq_4x, ftf_freq_5x = self.fundamental_train_frequency,self.fundamental_train_frequency*2,self.fundamental_train_frequency*3,self.fundamental_train_frequency*4,self.fundamental_train_frequency*5
        ftf_freq_1y, ftf_freq_2y, ftf_freq_3y, ftf_freq_4y, ftf_freq_5y = self.fundamental_train_frequency,self.fundamental_train_frequency*2,self.fundamental_train_frequency*3,self.fundamental_train_frequency*4,self.fundamental_train_frequency*5
        ftf_freq_1z, ftf_freq_2z, ftf_freq_3z, ftf_freq_4z, ftf_freq_5z = self.fundamental_train_frequency,self.fundamental_train_frequency*2,self.fundamental_train_frequency*3,self.fundamental_train_frequency*4,self.fundamental_train_frequency*5
        amp_vpf_1x,amp_vpf_1y, amp_vpf_1z, = 5.56,0.52,0.43
        freq_vpf_1x,freq_vpf_1y,freq_vpf_1z = self.vane_pass_frequency,self.vane_pass_frequency,self.vane_pass_frequency
        amp_vpf_lb_1x, amp_vpf_lb_1y, amp_vpf_lb_1z=5.74,0.48,0.37
        freq_vpf_lb_1x,freq_vpf_lb_1y,freq_vpf_lb_1z =self.vane_pass_frequency-self.rpm,self.vane_pass_frequency-self.rpm,self.vane_pass_frequency-self.rpm
        amp_vpf_rb_1x, amp_vpf_rb_1y, amp_vpf_rb_1z,=6,0.43,0.32
        freq_vpf_rb_1x,freq_vpf_rb_1y,freq_vpf_rb_1z =self.vane_pass_frequency+self.rpm,self.vane_pass_frequency+self.rpm,self.vane_pass_frequency+self.rpm
        # freq_1z,freq_2z,freq_3z,freq_4z,freq_5z=0,0,0,0,0
        no_of_noise_waves=1000
        amp_ul,freq_ul,amp_ll,freq_ll=1,self.required_sampling_rate/2,0,freq_2x+10
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'H_H_1_0.csv')
        healthy_equipment_df = pd.read_csv(file_path)
        vibration_healthy_equipment_df = healthy_equipment_df[['Accelerometer 1 (m/s^2)','Accelerometer 2 (m/s^2)','Accelerometer 3 (m/s^2)']]
        resampled_normal_data = self.resample_data(vibration_healthy_equipment_df,self.original_duration,self.required_duration,self.original_sampling_rate,self.required_sampling_rate)
        normal_with_random_data = self.generate_normal_data(resampled_normal_data)
        time_x,time_y,time_z = self.get_time_stamps(self.required_sampling_rate,self.required_duration)
        if(equipment_condition==None):
            fft_freq_x,fft_amp_x,fft_freq_y,fft_amp_y,fft_freq_z,fft_amp_z,ts_amp_x,ts_amp_y,ts_amp_z = self.get_freq_domain_data(normal_with_random_data,self.required_sampling_rate)
        elif(equipment_condition == "unbalance"):
            unbalance_data = self.generate_unbalance_data(normal_with_random_data,self.required_sampling_rate,self.required_duration,amp_1x,freq_1x,amp_1y,freq_1y,amp_1z,freq_1z)
            fft_freq_x,fft_amp_x,fft_freq_y,fft_amp_y,fft_freq_z,fft_amp_z,ts_amp_x,ts_amp_y,ts_amp_z = self.get_freq_domain_data(unbalance_data,self.required_sampling_rate)
        elif(equipment_condition == "misalignment"):
            misalignment_data = self.generate_misalignment_data(normal_with_random_data,self.required_sampling_rate,self.required_duration,amp_1x,freq_1x,amp_1y,freq_1y,amp_1z,freq_1z,amp_2x,freq_2x,amp_2y,freq_2y,amp_2z,freq_2z,amp_3x,freq_3x,amp_3y,freq_3y,amp_3z,freq_3z)
            fft_freq_x,fft_amp_x,fft_freq_y,fft_amp_y,fft_freq_z,fft_amp_z,ts_amp_x,ts_amp_y,ts_amp_z = self.get_freq_domain_data(misalignment_data,self.required_sampling_rate)
        elif(equipment_condition == "eccentricity"):
            eccentricity_data = self.generate_eccentricity_data(normal_with_random_data,self.required_sampling_rate,self.required_duration,amp_1x,freq_1x,amp_1y,freq_1y,amp_1z,freq_1z)
            fft_freq_x,fft_amp_x,fft_freq_y,fft_amp_y,fft_freq_z,fft_amp_z,ts_amp_x,ts_amp_y,ts_amp_z = self.get_freq_domain_data(eccentricity_data,self.required_sampling_rate)
        elif(equipment_condition == "bent_shaft"):
            bent_shaft_data = self.generate_bent_shaft_fault_data(normal_with_random_data, self.required_sampling_rate,self.required_duration, amp_1x, freq_1x, amp_1y, freq_1y, amp_1z, freq_1z,
                                        amp_2x, freq_2x, amp_2y, freq_2y, amp_2z, freq_2z)
            fft_freq_x,fft_amp_x,fft_freq_y,fft_amp_y,fft_freq_z,fft_amp_z,ts_amp_x,ts_amp_y,ts_amp_z = self.get_freq_domain_data(bent_shaft_data,self.required_sampling_rate)
        elif(equipment_condition == "innerrace_fault"):
            innerrace_fault_data = self.generate_innerracefault_data(normal_with_random_data, self.required_sampling_rate,self.required_duration, amp_1x, ir_freq_1x, amp_1y, ir_freq_1y, amp_1z, ir_freq_1z,
                                    amp_2x, ir_freq_2x, amp_2y, ir_freq_2y, amp_2z, ir_freq_2z,
                                    amp_3x, ir_freq_3x, amp_3y, ir_freq_3y, amp_3z, ir_freq_3z,
                                    amp_4x, ir_freq_4x, amp_4y, ir_freq_4y, amp_4z, ir_freq_4z,
                                    amp_5x, ir_freq_5x, amp_5y, ir_freq_5y, amp_5z, ir_freq_5z)
            fft_freq_x,fft_amp_x,fft_freq_y,fft_amp_y,fft_freq_z,fft_amp_z,ts_amp_x,ts_amp_y,ts_amp_z = self.get_freq_domain_data(innerrace_fault_data,self.required_sampling_rate)
        elif(equipment_condition == "outerrace_fault"):
            outerrace_fault_data = self.generate_outerracefault_data(normal_with_random_data,self.required_sampling_rate,self.required_duration,amp_1x,or_freq_1x,amp_1y,or_freq_1y,amp_1z,or_freq_1z,
                                                                    amp_2x,or_freq_2x,amp_2y,or_freq_2y,amp_2z,or_freq_2z,
                                                                    amp_3x,or_freq_3x,amp_3y,or_freq_3y,amp_3z,or_freq_3z,
                                                                    amp_4x,or_freq_4x,amp_4y,or_freq_4y,amp_4z,or_freq_4z,
                                                                    amp_5x,or_freq_5x,amp_5y,or_freq_5y,amp_5z,or_freq_5z)
            fft_freq_x,fft_amp_x,fft_freq_y,fft_amp_y,fft_freq_z,fft_amp_z,ts_amp_x,ts_amp_y,ts_amp_z = self.get_freq_domain_data(outerrace_fault_data,self.required_sampling_rate)
        elif(equipment_condition == "cage_fault"):
            cage_fault_data = self.generate_cagefault_data(normal_with_random_data,self.required_sampling_rate,self.required_duration, amp_1x, ftf_freq_1x, amp_1y, ftf_freq_1y, amp_1z, ftf_freq_1z,
                            amp_2x, ftf_freq_2x, amp_2y, ftf_freq_2y, amp_2z, ftf_freq_2z,
                            amp_3x, ftf_freq_3x, amp_3y, ftf_freq_3y, amp_3z, ftf_freq_3z,
                            amp_4x, ftf_freq_4x, amp_4y, ftf_freq_4y, amp_4z, ftf_freq_4z,
                            amp_5x, ftf_freq_5x, amp_5y, ftf_freq_5y, amp_5z, ftf_freq_5z)
            fft_freq_x,fft_amp_x,fft_freq_y,fft_amp_y,fft_freq_z,fft_amp_z,ts_amp_x,ts_amp_y,ts_amp_z = self.get_freq_domain_data(cage_fault_data,self.required_sampling_rate)
        elif(equipment_condition == "rolling_element_fault"):
            rolling_element_fault_data = self.generate_bearing_element_fault_data(normal_with_random_data, self.required_sampling_rate,self.required_duration, amp_1x, bsf_freq_1x, amp_1y, bsf_freq_1y, amp_1z, bsf_freq_1z,
                                        amp_2x, bsf_freq_2x, amp_2y, bsf_freq_2y, amp_2z, bsf_freq_2z,
                                        amp_3x, bsf_freq_3x, amp_3y, bsf_freq_3y, amp_3z, bsf_freq_3z,
                                        amp_4x, bsf_freq_4x, amp_4y, bsf_freq_4y, amp_4z, bsf_freq_4z,
                                        amp_5x, bsf_freq_5x, amp_5y, bsf_freq_5y, amp_5z, bsf_freq_5z)
            fft_freq_x,fft_amp_x,fft_freq_y,fft_amp_y,fft_freq_z,fft_amp_z,ts_amp_x,ts_amp_y,ts_amp_z = self.get_freq_domain_data(rolling_element_fault_data,self.required_sampling_rate)
        elif(equipment_condition == "starvation"):
            starvation_data = self.generate_starvation_fault_data(normal_with_random_data,self.required_sampling_rate,self.required_duration, amp_1x, freq_1x, amp_1y, freq_1y, amp_1z, freq_1z,
                                        amp_vpf_1x, freq_vpf_1x, amp_vpf_1y, freq_vpf_1y, amp_vpf_1z, freq_vpf_1z)
            fft_freq_x,fft_amp_x,fft_freq_y,fft_amp_y,fft_freq_z,fft_amp_z,ts_amp_x,ts_amp_y,ts_amp_z = self.get_freq_domain_data(starvation_data,self.required_sampling_rate)
        elif(equipment_condition == "broken_impeller"):
            broken_impeller_data = self.generate_broken_impeller_fault_data(normal_with_random_data, self.required_sampling_rate,self.required_duration, amp_vpf_1x, freq_vpf_1x, amp_vpf_1y, freq_vpf_1y, amp_vpf_1z, freq_vpf_1z,
                                            amp_vpf_lb_1x, freq_vpf_lb_1x, amp_vpf_lb_1y, freq_vpf_lb_1y, amp_vpf_lb_1z, freq_vpf_lb_1z,
                                            amp_vpf_rb_1x, freq_vpf_rb_1x, amp_vpf_rb_1y, freq_vpf_rb_1y, amp_vpf_rb_1z, freq_vpf_rb_1z)
            fft_freq_x,fft_amp_x,fft_freq_y,fft_amp_y,fft_freq_z,fft_amp_z,ts_amp_x,ts_amp_y,ts_amp_z = self.get_freq_domain_data(broken_impeller_data,self.required_sampling_rate)
        elif(equipment_condition == "cavitation"):
            cavitation_data = self.generate_cavitation_fault_data(normal_with_random_data,self.required_sampling_rate,self.required_duration,no_of_noise_waves,amp_ul,freq_ul,amp_ll,freq_ll)
            fft_freq_x,fft_amp_x,fft_freq_y,fft_amp_y,fft_freq_z,fft_amp_z,ts_amp_x,ts_amp_y,ts_amp_z = self.get_freq_domain_data(cavitation_data,self.required_sampling_rate)
        
        return fft_freq_x,fft_amp_x,fft_freq_y,fft_amp_y,fft_freq_z,fft_amp_z,ts_amp_x,ts_amp_y,ts_amp_z,time_x,time_y,time_z
   
   
   
   
   
   
   
   
    

    
    
    
    
    

    
    
    
        