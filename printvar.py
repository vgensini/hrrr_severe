#!/usr/local/python/2.7.2/bin/python
##################################################
#Purpose:  Plot images from Kim's WRF Files
#By: Victor Gensini - Summer 2014
##################################################
##IMPORT LIBRARIES################################
import matplotlib
##NEED THIS FOR CLUSTER USE#######################
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap,cm
import numpy as np
import Nio as pynio
import os
import textwrap
import datetime
import pygrib
##################################################
##DEFINE GLOBAL PATHS#############################
in_path = '/home/data/models/hrrr/1503191500F005.hrrr'
gr = pynio.open_file(in_path,mode='r',format='grb2') 
#uphly = gr.variables["VAR_0_7_199_P8_2L103_GLC0_max"][:]
#print uphly.shape
#new_grbs = pygrib.open(in_path)
x = gr.variables.keys()
print x
	
#new_grbs.seek(0)
#for grb in new_grbs:
#	print grb 
