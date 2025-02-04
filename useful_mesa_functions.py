import os

import numpy as np
import scipy as sp
import pandas as pd
import matplotlib.pyplot as plt
import sys

# logs_dir = sys.argv[1]

def load_history_file(logs_dir):
    return pd.read_table(os.path.join(logs_dir, 'history.data'), 
        skiprows=5, sep='\s+')

def get_index(logs_dir):
    return pd.read_table(os.path.join(logs_dir, 'profiles.index'), 
        names=['model_number', 'priority', 'profile_number'],
        skiprows=1, sep='\s+')

def get_history(logs_dir,profile_number):
    
    DF = load_history_file(logs_dir)
    index = get_index(logs_dir)

    model_number = index[index.profile_number == profile_number].model_number.values[0]

    return DF[DF.model_number == model_number]

def plot_HR(logs_dir, profile_number=-1):

    DF = load_history_file(logs_dir)
    index = get_index(logs_dir)

    plt.plot(10**DF['log_Teff'][1:], 
             10**DF['log_L'][1:], 
             lw=3, c='k', label='evolutionary track')
    
    first = 1
    for prof_num in index.profile_number:
        hist = get_history(logs_dir,prof_num)
        plt.plot(10**hist['log_Teff'], 10**hist['log_L'], '.',
                 c='r' if prof_num == profile_number else 'b', 
                 label=r'%0.2f Gyr' % (hist.star_age.values[0]/1e9)
                       if prof_num == profile_number else 'profile files' if first else '',
                 ms=10)
        if not prof_num == profile_number:
            first = 0
    
    plt.gca().invert_xaxis()
    plt.xlabel(r'effective temperature $T_{\rm{eff}}/\rm{K}$')
    plt.ylabel(r'luminosity $L/\rm{L}_\odot$')
    plt.xscale('log')
    plt.yscale('log')
    
    plt.legend()
    plt.title('HR Diagram', size=15)
    # plt.show()

def load_profile(logs_dir, profile_number):
    prof = pd.read_table(
        os.path.join(logs_dir, 'profile' + str(profile_number) + '.data'), 
        skiprows=5, sep='\s+')
    return prof

def get_profiles(logs_dir):

    index = get_index(logs_dir)

    return [load_profile(logs_dir, profile_number) 
            for profile_number in index.profile_number]

def plot_composition(logs_dir, profile_number, xaxis = 'radius'):

    profs = get_profiles(logs_dir)

    ZAMS_X = profs[0].x_mass_fraction_H.values[0]
    ZAMS_Y = profs[0].y_mass_fraction_He.values[0]
    Y_p = 0.2463

    prof = profs[profile_number-1]
    x = prof.mass #10**prof.logR / np.max(10**prof.logR)
    plt.plot(x, prof.x_mass_fraction_H, lw=3, label='hydrogen', c='k')
    plt.plot(x, prof.y_mass_fraction_He, lw=3, label='helium', c='b')
    plt.axhline(ZAMS_X, c='k', ls='--', zorder=-99)
    plt.axhline(ZAMS_Y, c='k', ls='--', zorder=-99)
    plt.axhline(Y_p, c='lightgray', ls='--', zorder=-99)
    plt.xlabel(r'mass coordinate')#plt.xlabel(r'fractional radius $r/R$')
    plt.ylabel(r'mass fraction')
    plt.legend()
    plt.title('Internal Composition', size=15)
    # plt.show()

from astropy.constants import G, M_sun
import astropy.units as u

def calculate_semi_major_axis_and_roche_lobe(m1_mass, mass_ratio, orbital_period_days):
    # Convert inputs to appropriate units
    m1 = m1_mass * M_sun  # Mass of the primary star in kg
    q = mass_ratio  # Mass ratio
    P = orbital_period_days * u.day  # Convert days to days unit
    
    # Calculate the mass of the secondary star
    m2 = q * m1  # Mass of the secondary star in kg
    
    # Total mass
    M_total = m1 + m2  # Total mass in kg
    
    # Calculate the semi-major axis using Kepler's Third Law
    a_cubed = (G * M_total * P**2) / (4 * np.pi**2)
    a = a_cubed**(1/3)  # Semi-major axis in meters
    
    # Convert semi-major axis to solar radii
    a_solar_radii = a.to(u.R_sun).value

    q_RL = 1/q
    
    # Calculate the Roche lobe radius for the primary star
    R_L = (0.49 * q_RL**(2/3) / (0.6 * q_RL**(2/3) + np.log(1 + q_RL**(1/3)))) * a  # in meters
    R_L_solar_radii = R_L.to(u.R_sun).value  # Convert to solar radii
    
    return a_solar_radii, R_L_solar_radii

