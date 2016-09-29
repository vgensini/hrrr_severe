#!/usr/bin/env python
##################################################
#Purpose:  HRRR Synthetic Severe Viewer
#By: Victor Gensini - Winter 2014
##################################################
##IMPORT LIBRARIES################################
import matplotlib
##NEED THIS FOR CLUSTER USE#######################
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap,cm
from matplotlib.path import Path
import numpy as np
import os
import pygrib
import datetime as dt
from osgeo import ogr
from osgeo import osr
from scipy.stats import itemfreq
##################################################
#ROMOVE OLD IMAGES
os.system('rm -f /home/apache/climate/gensini/synthetic/*.png')
##DEFINE GLOBAL PATHS#############################
in_path = '/home/data/models/hrrr/' #input data path
out_path = '/home/apache/climate/gensini/synthetic/' #output data path
begdate = dt.datetime.strptime(dt.datetime.utcnow().strftime('%Y%m%d%H'),"%Y%m%d%H") #Today's date YYYYMMDDHH
begdate = begdate-dt.timedelta(hours=0) #Start with a time previous to now
enddate = begdate+dt.timedelta(hours=15) #End with a time +15 hours from that time
dates = [] #List to store dates we need to loop through
while begdate < enddate: #create list of input dates
	#print begdate
	dates.append(begdate)
	begdate+=dt.timedelta(hours=1)

##################################################
##create zero arrays/variables to store reports###
hail_hrly_report_value = 0
hail_cumulative_report_value = 0
tor_hrly_report_value = 0
tor_cumulative_report_value = 0
wind_hrly_report_value = 0
wind_cumulative_report_value = 0
tor_count = np.zeros((1377,2145))
hail_count = np.zeros((1377,2145))
wind_count = np.zeros((1377,2145))
##################################################
#Set looping time variables
tim = dt.datetime.utcnow()-dt.timedelta(hours=1)
hr = tim.strftime('%H')
dy = tim.strftime('%d')
mn = tim.strftime('%m')
yr = tim.strftime('%y')
day = dt.datetime.utcnow().strftime('%B %d, %Y')

##GLOBAL BASEMAP VARIABLES########################
fig = plt.figure()
fig.set_size_inches(12.4,9)
fig.set_tight_layout(True)
plt.subplot(111)

CWAlist=[] #List of CWAs with synthetic reports
count = 1 #First forecast hour
for dt in dates: #begin loop for dates in dates list
	YY = dt.year
	MM = "%02d"%dt.month
	DD = "%02d"%dt.day
	HH = "%02d"%dt.hour
	in_file = yr+mn+dy+hr+'00F0'+str(count).zfill(2)+'.hrrr' #Create HRRR filename from date vriables
	filename_str = 'F0'+str(count).zfill(2)+'.hrrr' #Create output string name
	count += 1 #don't forget to add one to the counter!
	##OPEN GRIB FILE USING PYNIO######################
	grbs = pygrib.open(in_path+in_file) # open the grib file using pygrib
	for g in grbs:	#print the grib variables
		print g		#print the grib variables
	uvv = grbs.select(name='Hourly Maximum of Upward Vertical Velocity in the lowest 400hPa')[0] #read in uvv variable object
	max_reflectivity = grbs.select(name='Hourly Maximum of Simulated Reflectivity at 1 km AGL')[0].values
	windgust_values = grbs.select(name='Wind speed (gust)')[0].values
	reflectivity = grbs.select(name='Derived radar reflectivity')[0].values
	maxUH_values = grbs.select(name='Hourly Maximum of Updraft Helicity over Layer 2km to 5 km AGL')[0].values
	#get lat/lons and projection info for variable
	lats,lons = uvv.latlons()
	uvv_values = uvv.values
	#make basemap
	m = Basemap(projection='lcc',lat_0=38,lon_0=-97.5,llcrnrlat=22,urcrnrlat=48, llcrnrlon=-120,urcrnrlon=-62,resolution='l',area_thresh=100000.)
	m.drawcoastlines(color='gray',zorder=5)
	#m.drawstates(color='black',zorder=3)
	m.drawcountries(color='gray',zorder=4)
	#m.drawcounties(color='gray',zorder=3)
	m.readshapefile('/home/scripts/gensini/hrrr_severe/shapefiles/CWA',name='CWA',linewidth=0.5,zorder=4, color='Tan')
	#m.readshapefile('/home/scripts/gensini/hrrr_severe/shapefiles/US',name='US',linewidth=0.5,zorder=3, color='black')
	#m.drawlsmask(land_color='none',ocean_color='w',zorder=2)
	#parallels = np.arange(0.,90,5.)
	#m.drawparallels(parallels,labels=[1,0,0,0],color='DarkSlateGray',fontsize=10,zorder=6)
	#meridians = np.arange(180.,360.,5.)
	#m.drawmeridians(meridians,labels=[0,0,0,1],color='DarkSlateGray',fontsize=10,zorder=7)

    
	##WHAT FILE ARE WE CURRENTLY PROCESSING###########
	#print "Current file is: " + in_file

	x, y = m(lons, lats) #change lat/lon values into map projection coordinates
	
	##DECIDE WHAT A SYNTHETIC REPORT IS##
	#reports = np.array((refc>=45) & (uphly>=50),dtype=int) #decide what a synthetic report is
	hail_report = np.array((uvv_values>=40) & (uvv_values <200),dtype=int)
	hail_count = np.add(hail_count,hail_report)
	hail_hrly_report_value = (uvv_values>=20).sum()
	#print hrly_report_value
	hail_cumulative_report_value += hail_hrly_report_value
	hail_finlat = np.ma.masked_where(hail_report < 1, lats) #mask lat values if they do not have a report
	hail_finlon = np.ma.masked_where(hail_report < 1, lons) #mask lon values if they do not have a report
	hail_fincountlat = np.ma.masked_where(hail_count < 1, lats) #mask final lat values if they do not have a report
	hail_fincountlon = np.ma.masked_where(hail_count < 1, lons) #mask final lon values if they do not have a report
	
	hail_Mx,hail_My = m(hail_finlon,hail_finlat) #make marker and ID locations
	hail_FMx,hail_FMy = m(hail_fincountlon,hail_fincountlat)
	
	#hail_locs = plt.plot(hail_Mx,hail_My,marker='o',color='k',alpha=.1, markersize=8,zorder=4)
	hail_marks = plt.plot(hail_FMx,hail_FMy,marker='+',color='green',alpha=0,markersize=9, zorder=3)
	
	tor_report = np.array((maxUH_values>=100),dtype=int)
	tor_count = np.add(tor_count,tor_report)
	tor_hrly_report_value = (maxUH_values>=100).sum()
	#print hrly_report_value
	tor_cumulative_report_value += tor_hrly_report_value
	tor_finlat = np.ma.masked_where(tor_report < 1, lats) #mask lat values if they do not have a report
	tor_finlon = np.ma.masked_where(tor_report < 1, lons) #mask lon values if they do not have a report
	tor_fincountlat = np.ma.masked_where(tor_count < 1, lats) #mask final lat values if they do not have a report
	tor_fincountlon = np.ma.masked_where(tor_count < 1, lons) #mask final lon values if they do not have a report
	
	tor_Mx,tor_My = m(tor_finlon,tor_finlat) #make marker and ID locations
	tor_FMx,tor_FMy = m(tor_fincountlon,tor_fincountlat)
	
	#tor_locs = plt.plot(tor_Mx,tor_My,marker='o',color='k',alpha=.1, markersize=8,zorder=4)
	tor_marks = plt.plot(tor_FMx,tor_FMy,marker='+',color='red',alpha=0,markersize=9, zorder=3)
	
	wind_report = np.array((windgust_values>=25) & (max_reflectivity >=30),dtype=int)
	wind_count = np.add(wind_count,wind_report)
	wind_hrly_report_value = ((windgust_values>=25)& (max_reflectivity >=30)).sum()
	#print hrly_report_value
	wind_cumulative_report_value += wind_hrly_report_value
	wind_finlat = np.ma.masked_where(wind_report < 1, lats) #mask lat values if they do not have a report
	wind_finlon = np.ma.masked_where(wind_report < 1, lons) #mask lon values if they do not have a report
	wind_fincountlat = np.ma.masked_where(wind_count < 1, lats) #mask final lat values if they do not have a report
	wind_fincountlon = np.ma.masked_where(wind_count < 1, lons) #mask final lon values if they do not have a report
	
	wind_Mx,wind_My = m(wind_finlon,wind_finlat) #make marker and ID locations
	wind_FMx,wind_FMy = m(wind_fincountlon,wind_fincountlat)
	
	#wind_locs = plt.plot(wind_Mx,wind_My,marker='o',color='k',alpha=.1, markersize=8,zorder=4)
	wind_marks = plt.plot(wind_FMx,wind_FMy,marker='+',color='blue',alpha=0,markersize=9, zorder=3)
	
	repo_lat = np.extract(wind_report == 1,lats)
	repo_lon = np.extract(wind_report == 1,lons)
	
	
	
	def check(lon,lat): # Function to Check which CWA's have reports
		drv = ogr.GetDriverByName('ESRI Shapefile')
		ds_in = drv.Open('/home/scripts/gensini/hrrr_severe/shapefiles/CWA.shp')
		lyr_in = ds_in.GetLayer(0)
		idx_reg = lyr_in.GetLayerDefn().GetFieldIndex('CWA')
		pt = ogr.Geometry(ogr.wkbPoint)
		pt.SetPoint_2D(0,lon,lat)
		lyr_in.SetSpatialFilter(pt)
		for feat_in in lyr_in:
			ply = feat_in.GetGeometryRef()
			if ply.Contains(pt):
				CWAs = feat_in.GetFieldAsString(idx_reg)
				return CWAs

	
	for latty,lonny in zip(repo_lat,repo_lon):
		CWAs = check(lonny,latty)
		if CWAs == None:
			pass
		else:
			CWAlist.append(CWAs)
	final_CWA = itemfreq(CWAlist)
	#print final_CWA

	
	#print str(final_CWA[:,:])
	#while count < len(final_CWA):
	#if len(final_CWA) == 0:
		#bbox_props = dict(boxstyle="round", fc="k", ec="0.2", alpha=0)
		#plt.annotate('No CWAs with Synthetic Severe Weather',xycoords='figure fraction',xy=(.5,.9),color=('white'), ha="center", va="center", size=14.0,bbox=bbox_props,zorder=9)
	#if len(final_CWA) > 0:
		#bbox_props = dict(boxstyle="round", fc="k", ec="0.2", alpha=0)
		#plt.annotate('Gridpoints/CWA\n'+str(final_CWA[:,:]).replace('[',"").replace(']',"").replace("'",""),xycoords='figure fraction',xy=(.93,.5),color=('white'), ha="center", va="center", size=10.0,bbox=bbox_props,zorder=9)

	
	#NWS Reflectivity Colors
	nws_reflectivity_colors = ["#fdfdfd","#019ff4","#0300f4","#02fd02","#01c501","#008e00","#fdf802","#e5bc00","#fd9500","#fd0000","#d40000","#bc0000","#f800fd","#9854c6"]
	cmap = matplotlib.colors.ListedColormap(nws_reflectivity_colors)
	#MAP INTERVALS
	intervals = np.arange(0,75,5)
	#MAKE MESH MAP
	refc_map = m.pcolormesh(x,y,np.ma.masked_where(reflectivity>=-9999, reflectivity),shading='flat',vmin=0,vmax=70,cmap=cmap,zorder=1)
	#MAKE COLORBAR
	colbar = m.colorbar(refc_map,"bottom",size="2%",ticks=intervals)
	#MAKE COLORBAR LABEL
	colbar.set_label('Simulated Radar Reflectivity Factor (dBZ)',fontsize=12, alpha=0)
	#MAKE TITLE
	plt.title(hr+'Z HRRR 1KM Reflectivity valid %s/%s/%s %sZ' % (MM,DD,YY,HH), fontsize=16, alpha=0)
	plt.annotate('Total Gridpoints: '+str(tor_cumulative_report_value),xycoords='figure pixels',xy=(1355,27),color=('purple'), size=10, alpha=0)
	plt.annotate('Hourly Gridpoints: '+str(tor_hrly_report_value),xycoords='figure pixels',xy=(1095,27),color=('purple'), size=10, alpha=0)
	plt.annotate('Victor Gensini @gensiniwx',xycoords='figure pixels',xy=(122,27), color=('darkred'),size=10, alpha=0)
	plt.subplots_adjust(left=None,right=None,top=None,bottom=None,wspace=None,hspace=None)
	
	#SAVE FIGURE
	plt.savefig('CWA.png',dpi=100, transparent=True)
	plt.clf()
	#del report
	tor_report = np.zeros((1377,2145))
	hail_report = np.zeros((1377,2145))
	wind_report = np.zeros((1377,2145)) #reset counter array

