#!/usr/bin/env python
__author__ = 'Mike McCann,Duane Edgington,Danelle Cline'
__copyright__ = '2018'
__license__ = 'GPL v3'
__contact__ = 'duane at mbari.org'

__doc__ = '''

Master loader for all CANON May-June Campaign 2018

Mike McCann, Duane Edgington, Danelle Cline
MBARI 15 May 2018

@var __date__: Date of last svn commit
@undocumented: __doc__ parser
@status: production
@license: GPL
'''

import os
import sys
import datetime  # needed for glider data
import time  # for startdate, enddate args
import csv
import urllib2
import urlparse
import requests

parentDir = os.path.join(os.path.dirname(__file__), "../")
sys.path.insert(0, parentDir)  # So that CANON is found

from CANON import CANONLoader
from loaders import FileNotFound
from thredds_crawler.crawl import Crawl
from thredds_crawler.etree import etree

cl = CANONLoader('stoqs_canon_may2018', 'CANON - May June 2018',
                 description='May June 2018 campaign observations in Monterey Bay',
                 x3dTerrains={
                   'http://dods.mbari.org/terrain/x3d/Monterey25_10x/Monterey25_10x_scene.x3d': {
                     'position': '-2822317.31255 -4438600.53640 3786150.85474',
                     'orientation': '0.89575 -0.31076 -0.31791 1.63772',
                     'centerOfRotation': '-2711557.9403829873 -4331414.329506527 3801353.4691465236',
                     'VerticalExaggeration': '10',
                   },
                   'http://stoqs.mbari.org/x3d/Monterey25_1x/Monterey25_1x_src_scene.x3d': {
                     'name': 'Monterey25_1x',
                     'position': '-2822317.31255 -4438600.53640 3786150.85474',
                     'orientation': '0.89575 -0.31076 -0.31791 1.63772',
                     'centerOfRotation': '-2711557.9403829873 -4331414.329506527 3801353.4691465236',
                     'VerticalExaggeration': '1',
                   },
                 },
                 grdTerrain=os.path.join(parentDir, 'Monterey25.grd')
                 )

# Set start and end dates for all loads from sources that contain data
# beyond the temporal bounds of the campaign
#
startdate = datetime.datetime(2018, 5, 15)  # Fixed start. May 15, 2018
enddate = datetime.datetime(2018, 6, 15)  # Fixed end. June 15, 2018.

# default location of thredds and dods data:
cl.tdsBase = 'http://odss.mbari.org/thredds/'
cl.dodsBase = cl.tdsBase + 'dodsC/'


#####################################################################
#  DORADO
#####################################################################
# special location for dorado data
cl.dorado_base = 'http://dods.mbari.org/opendap/data/auvctd/surveys/2018/netcdf/'
cl.dorado_files = [
                   'Dorado389_2018_156_00_156_00_decim.nc',
                   'Dorado389_2018_164_00_164_00_decim.nc',

                  ]
cl.dorado_parms = [ 'temperature', 'oxygen', 'nitrate', 'bbp420', 'bbp700',
                    'fl700_uncorr', 'salinity', 'biolume',
                    'sepCountList', 'mepCountList',
                    'roll', 'pitch', 'yaw',
                  ]

#####################################################################
#  LRAUV
#####################################################################
def find_urls(base, search_str):
    INV_NS = "http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0"
    url = os.path.join(base, 'catalog.xml')
    print "Crawling: %s" % url
    skips = Crawl.SKIPS + [".*Courier*", ".*Express*", ".*Normal*, '.*Priority*", ".*.cfg$" ]
    u = urlparse.urlsplit(url)
    name, ext = os.path.splitext(u.path)
    if ext == ".html":
        u = urlparse.urlsplit(url.replace(".html", ".xml"))
    url = u.geturl()
    urls = []
    # Get an etree object
    try:
        r = requests.get(url)
        tree = etree.XML(r.text.encode('utf-8'))

        # Crawl the catalogRefs:
        for ref in tree.findall('.//{%s}catalogRef' % INV_NS):

            try:
                # get the mission directory name and extract the start and ending dates
                mission_dir_name = ref.attrib['{http://www.w3.org/1999/xlink}title']
                dts = mission_dir_name.split('_')
                dir_start =  datetime.datetime.strptime(dts[0], '%Y%m%d')
                dir_end =  datetime.datetime.strptime(dts[1], '%Y%m%d')

                # if within a valid range, grab the valid urls
                if dir_start >= startdate and dir_end <= enddate:

                    print 'Found mission directory ' + dts[0]
                    print 'Searching if within range %s and %s  %s %s' % (startdate, enddate, dir_start, dir_end)
                    catalog = ref.attrib['{http://www.w3.org/1999/xlink}href']
                    c = Crawl(os.path.join(base, catalog), select=[search_str], skip=skips)
                    d = [s.get("url") for d in c.datasets for s in d.services if s.get("service").lower() == "opendap"]
                    for url in d:
                        urls.append(url)
            except Exception as ex:
                print "Error reading mission directory name %s" % ex

    except BaseException:
        print "Skipping %s (error parsing the XML)" % url

    if not urls:
        raise FileNotFound('No urls matching "{}" found in {}'.format(search_str, os.path.join(base, 'catalog.html')))

    return urls

# Load netCDF files produced (binned, etc.) by Danelle Cline
# These binned files are created with the makeLRAUVNetCDFs.sh script in the
# toNetCDF directory. You must first edit and run that script once to produce
# the binned files before this will work

# Get directory list from thredds server
platforms = ['tethys', 'aku', 'makai', 'ahi', 'opah', 'daphne']


for p in platforms:
    base =  'http://dods.mbari.org/thredds/catalog/LRAUV/' + p + '/missionlogs/2018/'
    dods_base = 'http://dods.mbari.org/opendap/data/lrauv/' + p + '/missionlogs/2018/'
    setattr(cl, p + '_files', [])
    setattr(cl, p + '_base', dods_base)
    setattr(cl, p + '_parms' , ['temperature', 'salinity', 'chlorophyll', 'nitrate', 'oxygen','bbp470', 'bbp650','PAR',
                                'yaw', 'pitch', 'roll', 'control_inputs_rudder_angle', 'control_inputs_mass_position',
                                'control_inputs_buoyancy_position', 'control_inputs_propeller_rotation_rate',
                                'health_platform_battery_charge', 'health_platform_average_voltage',
                                'health_platform_average_current','fix_latitude', 'fix_longitude',
                                'fix_residual_percent_distance_traveled_DeadReckonUsingSpeedCalculator',
                                'pose_longitude_DeadReckonUsingSpeedCalculator',
                                'pose_latitude_DeadReckonUsingSpeedCalculator',
                                'pose_depth_DeadReckonUsingSpeedCalculator',
                                'fix_residual_percent_distance_traveled_DeadReckonUsingMultipleVelocitySources',
                                'pose_longitude_DeadReckonUsingMultipleVelocitySources',
                                'pose_latitude_DeadReckonUsingMultipleVelocitySources',
                                'pose_depth_DeadReckonUsingMultipleVelocitySources'])
    try:
        #urls_eng = find_urls(base, '.*2S_eng.nc$')
        urls_sci = find_urls(base, '.*10S_sci.nc$')
        urls = urls_sci# + urls_eng
        files = []
        if len(urls) > 0 :
            for url in sorted(urls):
                file = '/'.join(url.split('/')[-3:])
                files.append(file)
            setattr(cl, p + '_files', files)

        setattr(cl, p  + '_startDatetime', startdate)
        setattr(cl, p + '_endDatetime', enddate)

    except FileNotFound:
        continue

######################################################################
#  GLIDERS
######################################################################
# Glider data files from CeNCOOS thredds server
# L_662a updated parameter names in netCDF file
cl.l_662a_base = 'http://legacy.cencoos.org/thredds/dodsC/gliders/Line66/'
cl.l_662a_files = [
                   'OS_Glider_L_662_20180430_TS.nc',
                  ]
cl.l_662a_parms = ['temperature', 'salinity', 'fluorescence','oxygen']
cl.l_662a_startDatetime = startdate
cl.l_662a_endDatetime = enddate

# NPS_34a updated parameter names in netCDF file
## The following loads decimated subset of data telemetered during deployment
cl.nps34a_base = 'http://legacy.cencoos.org/thredds/dodsC/gliders/Line66/'
cl.nps34a_files = [ 'OS_Glider_NPS_G34_20180514_TS.nc' ]
cl.nps34a_parms = ['temperature', 'salinity','fluorescence']
cl.nps34a_startDatetime = startdate
cl.nps34a_endDatetime = enddate

# Slocum Teledyne nemesis Glider
## from ioos site ## these files proved to be not compatible with python loader
## cl.slocum_nemesis_base = 'https://data.ioos.us/gliders/thredds/dodsC/deployments/mbari/Nemesis-20170412T0000/'
## cl.slocum_nemesis_files = [ 'Nemesis-20170412T0000.nc3.nc' ]
##   from cencoos directory, single non-aggregated files
cl.slocum_nemesis_base = 'http://legacy.cencoos.org/thredds/dodsC/gliders/Line66/Nemesis/nemesis_201805/'

cl.slocum_nemesis_files = [
        'nemesis_20180615T125540_rt0.nc',
        'nemesis_20180615T110755_rt0.nc',
        'nemesis_20180615T055202_rt0.nc',
        'nemesis_20180615T040529_rt0.nc',
        'nemesis_20180614T223834_rt0.nc',
        'nemesis_20180614T204944_rt0.nc',
        'nemesis_20180614T152947_rt0.nc',
        'nemesis_20180614T134039_rt0.nc',
        'nemesis_20180614T081728_rt0.nc',
        'nemesis_20180614T063243_rt0.nc',
        'nemesis_20180614T012635_rt0.nc',
        'nemesis_20180613T232915_rt0.nc',
        'nemesis_20180613T221715_rt0.nc',
        'nemesis_20180613T220144_rt0.nc',
        'nemesis_20180613T201011_rt0.nc',
        'nemesis_20180613T185429_rt0.nc',
        'nemesis_20180613T175426_rt0.nc',
        'nemesis_20180613T173402_rt0.nc',
        'nemesis_20180613T163823_rt0.nc',
        'nemesis_20180613T162255_rt0.nc',
        'nemesis_20180613T121009_rt0.nc',
        'nemesis_20180613T103624_rt0.nc',
        'nemesis_20180613T045607_rt0.nc',
        'nemesis_20180613T031617_rt0.nc',
        'nemesis_20180612T215444_rt0.nc',
        'nemesis_20180612T200659_rt0.nc',
        'nemesis_20180612T144752_rt0.nc',
        'nemesis_20180612T130014_rt0.nc',
        'nemesis_20180612T073153_rt0.nc',
        'nemesis_20180612T054113_rt0.nc',
        'nemesis_20180612T002011_rt0.nc',
        'nemesis_20180611T223126_rt0.nc',
        'nemesis_20180611T171414_rt0.nc',
        'nemesis_20180611T152528_rt0.nc',
        'nemesis_20180611T100045_rt0.nc',
        'nemesis_20180611T081500_rt0.nc',

        'nemesis_20180611T024956_rt0.nc',
        'nemesis_20180611T005810_rt0.nc',
        'nemesis_20180610T211730_rt0.nc',
        'nemesis_20180610T173357_rt0.nc',
        'nemesis_20180610T121911_rt0.nc',
        'nemesis_20180610T103323_rt0.nc',
        'nemesis_20180610T051627_rt0.nc',
        'nemesis_20180610T032549_rt0.nc',
        'nemesis_20180609T221221_rt0.nc',
        'nemesis_20180609T202615_rt0.nc',
        'nemesis_20180609T145306_rt0.nc',
        'nemesis_20180609T130822_rt0.nc',
        'nemesis_20180609T074007_rt0.nc',
        'nemesis_20180609T055722_rt0.nc',
        'nemesis_20180609T003722_rt0.nc',
        'nemesis_20180608T224831_rt0.nc',
        'nemesis_20180608T175945_rt0.nc',
        'nemesis_20180608T164334_rt0.nc',
        'nemesis_20180608T143658_rt0.nc',
        'nemesis_20180608T120708_rt0.nc',
        'nemesis_20180608T110933_rt0.nc',
        'nemesis_20180608T083441_rt0.nc',
        'nemesis_20180608T073206_rt0.nc',
        'nemesis_20180608T051449_rt0.nc',
        'nemesis_20180608T043216_rt0.nc',
        'nemesis_20180608T014701_rt0.nc',
        'nemesis_20180608T005828_rt0.nc',
        'nemesis_20180607T210404_rt0.nc',
        'nemesis_20180607T204644_rt0.nc',
        'nemesis_20180607T184820_rt0.nc',
        'nemesis_20180607T170239_rt0.nc',

        'nemesis_20180607T141543_rt0.nc',
        'nemesis_20180607T124757_rt0.nc',
        'nemesis_20180607T084329_rt0.nc',
        'nemesis_20180607T072152_rt0.nc',
        'nemesis_20180607T031016_rt0.nc',
        'nemesis_20180607T014837_rt0.nc',
        'nemesis_20180606T202458_rt0.nc',
        'nemesis_20180606T183115_rt0.nc',

        'nemesis_20180606T132359_rt0.nc',
        'nemesis_20180606T113615_rt0.nc',
        'nemesis_20180606T061921_rt0.nc',
        'nemesis_20180606T043043_rt0.nc',
        'nemesis_20180605T231000_rt0.nc',
        'nemesis_20180605T212118_rt0.nc',
        'nemesis_20180605T155935_rt0.nc',
        'nemesis_20180605T141014_rt0.nc',
        'nemesis_20180605T085233_rt0.nc',
        'nemesis_20180605T070154_rt0.nc',
        'nemesis_20180605T031744_rt0.nc',
        'nemesis_20180604T233637_rt0.nc',
        'nemesis_20180604T181842_rt0.nc',
        'nemesis_20180604T163244_rt0.nc',
        'nemesis_20180604T092308_rt0.nc',
        'nemesis_20180604T040607_rt0.nc',
        'nemesis_20180604T022123_rt0.nc',
        'nemesis_20180603T210413_rt0.nc',
        'nemesis_20180603T191831_rt0.nc',
        'nemesis_20180603T140517_rt0.nc',
        'nemesis_20180603T121929_rt0.nc',
        'nemesis_20180603T071759_rt0.nc',
        'nemesis_20180603T052610_rt0.nc',
        'nemesis_20180603T031009_rt0.nc',
        'nemesis_20180603T022738_rt0.nc',
        'nemesis_20180602T233110_rt0.nc',
        'nemesis_20180602T204803_rt0.nc',
        'nemesis_20180602T183615_rt0.nc',
        'nemesis_20180602T175305_rt0.nc',
        'nemesis_20180602T150336_rt0.nc',
        'nemesis_20180602T140859_rt0.nc',
        'nemesis_20180602T090410_rt0.nc',
        'nemesis_20180602T071934_rt0.nc',
        'nemesis_20180602T015811_rt0.nc',
        'nemesis_20180602T001228_rt0.nc',
        'nemesis_20180601T185917_rt0.nc',
        'nemesis_20180601T171007_rt0.nc',
        'nemesis_20180601T115021_rt0.nc',
        'nemesis_20180601T100739_rt0.nc',
        'nemesis_20180601T044606_rt0.nc',
        'nemesis_20180601T025827_rt0.nc',
        'nemesis_20180601T003121_rt0.nc',
        'nemesis_20180531T224240_rt0.nc',
        'nemesis_20180531T172008_rt0.nc',
        'nemesis_20180531T153237_rt0.nc',
        'nemesis_20180531T101932_rt0.nc',
        'nemesis_20180531T082452_rt0.nc',
        'nemesis_20180531T045057_rt0.nc',
        'nemesis_20180530T231216_rt0.nc',
        'nemesis_20180530T212637_rt0.nc',
        'nemesis_20180530T153412_rt0.nc',
        'nemesis_20180530T134513_rt0.nc',
        'nemesis_20180530T081406_rt0.nc',
        'nemesis_20180530T062523_rt0.nc',
        'nemesis_20180530T004850_rt0.nc',
        'nemesis_20180529T225710_rt0.nc',
        'nemesis_20180529T152223_rt0.nc',
        'nemesis_20180529T172607_rt0.nc',
        'nemesis_20180529T092011_rt0.nc',  
        'nemesis_20180529T073732_rt0.nc',      
        'nemesis_20180529T035307_rt0.nc',
        'nemesis_20180529T002221_rt0.nc',
        'nemesis_20180528T223642_rt0.nc',
        'nemesis_20180528T172045_rt0.nc',
        'nemesis_20180528T153313_rt0.nc',
        'nemesis_20180528T101737_rt0.nc',
        'nemesis_20180528T083156_rt0.nc',
        'nemesis_20180528T031438_rt0.nc',
        'nemesis_20180528T012900_rt0.nc',
        'nemesis_20180527T200926_rt0.nc',
        'nemesis_20180527T182323_rt0.nc',
        'nemesis_20180527T130348_rt0.nc',
        'nemesis_20180527T111807_rt0.nc',
        'nemesis_20180527T060038_rt0.nc',
        'nemesis_20180527T041500_rt0.nc',
        'nemesis_20180526T225705_rt0.nc',
        'nemesis_20180526T211127_rt0.nc',
        'nemesis_20180526T155125_rt0.nc',
        'nemesis_20180526T140052_rt0.nc',
        'nemesis_20180526T083551_rt0.nc',
        'nemesis_20180526T065013_rt0.nc',
        'nemesis_20180526T013514_rt0.nc',
        'nemesis_20180525T234931_rt0.nc',
        'nemesis_20180525T182645_rt0.nc',
        'nemesis_20180525T163804_rt0.nc',
        'nemesis_20180525T111958_rt0.nc',
        'nemesis_20180525T093117_rt0.nc',
        'nemesis_20180525T054532_rt0.nc',
        'nemesis_20180525T020511_rt0.nc',
        'nemesis_20180524T204810_rt0.nc',
        'nemesis_20180524T185653_rt0.nc',
        'nemesis_20180524T132921_rt0.nc',
        'nemesis_20180524T114042_rt0.nc',
        'nemesis_20180524T075617_rt0.nc',
        'nemesis_20180524T041131_rt0.nc',
        'nemesis_20180523T223811_rt0.nc',
        'nemesis_20180523T204655_rt0.nc',
        'nemesis_20180523T170354_rt0.nc',
        'nemesis_20180523T132421_rt0.nc',  
        'nemesis_20180523T094436_rt0.nc',  
        'nemesis_20180523T060002_rt0.nc',   
        'nemesis_20180523T022234_rt0.nc',   
        'nemesis_20180522T223930_rt0.nc',   
        'nemesis_20180522T185629_rt0.nc',   
        'nemesis_20180522T151002_rt0.nc',   
        'nemesis_20180522T112729_rt0.nc',   
        'nemesis_20180522T074822_rt0.nc',   
        'nemesis_20180522T040721_rt0.nc',   
        'nemesis_20180522T002128_rt0.nc',   
        'nemesis_20180521T203710_rt0.nc',   
        'nemesis_20180521T165515_rt0.nc',
        'nemesis_20180521T130842_rt0.nc',
        'nemesis_20180521T092215_rt0.nc',
        'nemesis_20180521T070845_rt0.nc',
        'nemesis_20180521T032301_rt0.nc',
        'nemesis_20180520T234041_rt0.nc',
        'nemesis_20180520T195820_rt0.nc',
        'nemesis_20180520T161902_rt0.nc',
        'nemesis_20180520T123557_rt0.nc',
        'nemesis_20180520T085329_rt0.nc',
        'nemesis_20180520T051403_rt0.nc',
        'nemesis_20180520T015451_rt0.nc',
        'nemesis_20180519T225042_rt0.nc',
        'nemesis_20180519T190448_rt0.nc',
        'nemesis_20180519T152606_rt0.nc',
        'nemesis_20180519T114451_rt0.nc',
        'nemesis_20180519T075753_rt0.nc',
        'nemesis_20180519T041218_rt0.nc',
        'nemesis_20180519T002744_rt0.nc',
        'nemesis_20180518T163902_rt0.nc',
        'nemesis_20180518T125641_rt0.nc',
        'nemesis_20180518T085931_rt0.nc',
        'nemesis_20180518T051145_rt0.nc',
        'nemesis_20180518T014253_rt0.nc',
        'nemesis_20180517T202400_rt0.nc',
        'nemesis_20180517T200241_rt0.nc',
        'nemesis_20180517T194759_rt0.nc',
        'nemesis_20180517T190408_rt0.nc',
        'nemesis_20180517T184216_rt0.nc',
        'nemesis_20180517T182705_rt0.nc',
        'nemesis_20180517T172155_rt0.nc',
        'nemesis_20180517T165640_rt0.nc',
        'nemesis_20180517T164435_rt0.nc',
        'nemesis_20180517T125058_rt0.nc',
        'nemesis_20180517T094903_rt0.nc',
        'nemesis_20180517T055003_rt0.nc',
        'nemesis_20180517T020552_rt0.nc',
        'nemesis_20180516T221356_rt0.nc',
        'nemesis_20180516T185907_rt0.nc',
        'nemesis_20180516T151154_rt0.nc',
        'nemesis_20180516T122932_rt0.nc',
        'nemesis_20180516T092727_rt0.nc',
        'nemesis_20180516T073726_rt0.nc',
        'nemesis_20180516T062621_rt0.nc',
        'nemesis_20180516T045411_rt0.nc',
        'nemesis_20180516T043058_rt0.nc',
        'nemesis_20180516T030956_rt0.nc',
        'nemesis_20180516T014746_rt0.nc',
        'nemesis_20180516T005405_rt0.nc',
        'nemesis_20180515T231601_rt0.nc',
        'nemesis_20180515T223800_rt0.nc',
        'nemesis_20180515T211255_rt0.nc',
        'nemesis_20180515T202553_rt0.nc',
                          ]
cl.slocum_nemesis_parms = [ 'temperature', 'salinity', 'u', 'v' ] #'oxygen', 'cdom', 'opbs', 'fluorescence' not populated
cl.slocum_nemesis_startDatetime = startdate
cl.slocum_nemesis_endDatetime = enddate


######################################################################
# Wavegliders
######################################################################
# WG Tex - All instruments combined into one file - one time coordinate
##cl.wg_tex_base = cl.dodsBase + 'CANON_september2013/Platforms/Gliders/WG_Tex/final/'
##cl.wg_tex_files = [ 'WG_Tex_all_final.nc' ]
##cl.wg_tex_parms = [ 'wind_dir', 'wind_spd', 'atm_press', 'air_temp', 'water_temp', 'sal', 'density', 'bb_470', 'bb_650', 'chl' ]
##cl.wg_tex_startDatetime = startdate
##cl.wg_tex_endDatetime = enddate

# WG Sparky - All instruments combined into one file - one time coordinate
cl.wg_Sparky_base = 'http://dods.mbari.org/opendap/data/waveglider/deployment_data/'
cl.wg_Sparky_files = [
                      'wgSparky/20180531/realTime/20180531.nc',
                     ]

cl.wg_Sparky_parms = [ 'wind_dir', 'avg_wind_spd', 'max_wind_spd', 'atm_press', 'air_temp', 'water_temp_float', 'sal_float',  "water_temp_sub', 
                     'sal_sub', 'bb_470', 'bb_650', 'chl', 'beta_470', 'beta_650', 'pH', 'O2_conc' ] # two ctds (_float, _sub), no CO2
cl.wg_Sparky_depths = [ 0 ]
cl.wg_Sparky_startDatetime = startdate
cl.wg_Sparky_endDatetime = enddate

# WG Tiny - All instruments combined into one file - one time coordinate
cl.wg_Tiny_base = 'http://dods.mbari.org/opendap/data/waveglider/deployment_data/'
cl.wg_Tiny_files = [
                      'wgTiny/20180516/realTime/20180516.nc',
                   ]


cl.wg_Tiny_parms = [ 'wind_dir', 'avg_wind_spd', 'max_wind_spd', 'atm_press', 'air_temp', 'water_temp', 'sal',  'bb_470', 'bb_650', 'chl',
                    'beta_470', 'beta_650', 'pCO2_water', 'pCO2_air', 'pH', 'O2_conc' ]
cl.wg_Tiny_depths = [ 0 ]
cl.wg_Tiny_startDatetime = startdate
cl.wg_Tiny_endDatetime = enddate

# WG OA - All instruments combined into one file - one time coordinate
##cl.wg_oa_base = cl.dodsBase + 'CANON/2015_OffSeason/Platforms/Waveglider/wgOA/'
##cl.wg_oa_files = [ 'Sept_2013_OAWaveglider_final.nc' ]
##cl.wg_oa_parms = [ 'distance', 'wind_dir', 'avg_wind_spd', 'max_wind_spd', 'atm_press', 'air_temp', 'water_temp', 'sal', 'O2_conc',
##                   'O2_sat', 'beta_470', 'bb_470', 'beta_700', 'bb_700', 'chl', 'pCO2_water', 'pCO2_air', 'pH' ]
##cl.wg_oa_startDatetime = startdate
##cl.wg_oa_endDatetime = enddate

######################################################################
#  MOORINGS
######################################################################
cl.m1_base = 'http://dods.mbari.org/opendap/data/ssdsdata/deployments/m1/'
cl.m1_files = [
  '201708/OS_M1_20170808hourly_CMSTV.nc',]
cl.m1_parms = [
  'eastward_sea_water_velocity_HR', 'northward_sea_water_velocity_HR',
  'SEA_WATER_SALINITY_HR', 'SEA_WATER_TEMPERATURE_HR', 'SW_FLUX_HR', 'AIR_TEMPERATURE_HR',
  'EASTWARD_WIND_HR', 'NORTHWARD_WIND_HR', 'WIND_SPEED_HR'
]

cl.m1_startDatetime = startdate
cl.m1_endDatetime = enddate

# Mooring 0A1
cl.oa1_base = 'http://dods.mbari.org/opendap/data/oa_moorings/deployment_data/OA1/201607/realTime/'
cl.oa1_files = [
               'OA1_201607.nc'
               ]
cl.oa1_parms = [
               'wind_dir', 'avg_wind_spd', 'atm_press', 'air_temp', 'water_temp',
               'sal', 'O2_conc', 'chl', 'pCO2_water', 'pCO2_air', 'pH',
               ]
cl.oa1_startDatetime = startdate
cl.oa1_endDatetime = enddate

# Mooring 0A2
cl.oa2_base = 'http://dods.mbari.org/opendap/data/oa_moorings/deployment_data/OA2/201609/'
cl.oa2_files = [
               'realTime/OA2_201609.nc'
               ]
cl.oa2_parms = [
               'wind_dir', 'avg_wind_spd', 'atm_press', 'air_temp', 'water_temp',
               'sal', 'O2_conc', 'chl', 'pCO2_water', 'pCO2_air', 'pH',
               ]
cl.oa2_startDatetime = startdate
cl.oa2_endDatetime = enddate


######################################################################
#  RACHEL CARSON: Jan 2017 --
######################################################################
# UCTD
cl.rcuctd_base = cl.dodsBase + 'Other/routine/Platforms/Ships/RachelCarson/uctd/'
cl.rcuctd_parms = [ 'TEMP', 'PSAL', 'xmiss', 'wetstar' ]
cl.rcuctd_files = [
#                  '00917plm01.nc',
#                  '03917plm01.nc',
                  ]

# PCTD
cl.rcpctd_base = cl.dodsBase + 'Other/routine/Platforms/Ships/RachelCarson/pctd/'
cl.rcpctd_parms = [ 'TEMP', 'PSAL', 'xmiss', 'ecofl', 'oxygen' ]
cl.rcpctd_files = [
#                  '00917c01.nc', '00917c02.nc', '00917c03.nc',
#                  '03917c01.nc', '03917c02.nc', '03917c03.nc',
                  ]

######################################################################
#  WESTERN FLYER: Apr 2017 --
######################################################################
# UCTD
cl.wfuctd_base = cl.dodsBase + 'Other/routine/Platforms/Ships/WesternFlyer/uctd/'
cl.wfuctd_parms = [ 'TEMP', 'PSAL', 'xmiss', 'wetstar' ]
cl.wfuctd_files = [
                  'canon17sm01.nc',
                  ]

# PCTD
cl.wfpctd_base = cl.dodsBase + 'Other/routine/Platforms/Ships/WesternFlyer/pctd/'
cl.wfpctd_parms = [ 'TEMP', 'PSAL', 'xmiss', 'ecofl', 'oxygen' ]
cl.wfpctd_files = [
                  'canon17sc01.nc',
                  ]

###################################################################################################
# SubSample data files from /mbari/BOG_Archive/ReportsForSTOQS/
#   copied to local BOG_Data/CANON_OS2107 dir
###################################################################################################
cl.subsample_csv_base = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'BOG_Data/CANON_OS2017/bctd/')
cl.subsample_csv_files = [
##   'STOQS_00917_OXY_PS.csv',
##   'STOQS_00917_CARBON_GFF.csv',
##   'STOQS_00917_CHL_1U.csv',    'STOQS_00917_FLUOR.csv',
##   'STOQS_00917_CHL_5U.csv', 'STOQS_00917_NH4.csv', 'STOQS_00917_PHAEO_1U.csv',
##   'STOQS_00917_CHLA.csv', 'STOQS_00917_O2.csv', 'STOQS_00917_PHAEO_5U.csv',
##   'STOQS_00917_CHL_GFF.csv',
##   'STOQS_00917_PHAEO_GFF.csv',
                       ]

# Execute the load
cl.process_command_line()

if cl.args.test:

    cl.loadM1(stride=100)
    cl.loadTethys(stride=100)
    cl.loadL_662(stride=100)
    cl.loadAhi(stride=100)
    cl.loadAku(stride=100)
    cl.loadOpah(stride=100)
    cl.loadL_662(stride=100)
    cl.loadL_662a(stride=100)
    cl.load_NPS34(stride=100)
    cl.load_NPS34a(stride=100)
    cl.load_slocum_nemesis(stride=100)
    cl.load_SG621(stride=100) ## KISS glider
    cl.load_SG539(stride=100) ## KISS glider
    cl.load_wg_Tiny(stride=100)
    cl.load_oa1(stride=100)
    cl.load_oa2(stride=100)
    cl.loadDorado(stride=100)
    ##cl.loadDaphne(stride=100)
    ##cl.loadMakai(stride=100)
    cl.loadRCuctd(stride=100)
    cl.loadRCpctd(stride=100)
    cl.loadWFuctd(stride=100)
    cl.loadWFpctd(stride=100)

    cl.loadSubSamples()

elif cl.args.optimal_stride:

    cl.loadL_662(stride=2)
    ##cl.load_NPS29(stride=2)
    #cl.load_NPS34(stride=2)
    cl.load_wg_Tiny(stride=2)
    cl.load_oa1(stride=2)
    cl.load_oa2(stride=2)
    cl.loadM1(stride=2)
    ##cl.loadDorado(stride=2)
    cl.loadRCuctd(stride=2)
    cl.loadRCpctd(stride=2)

    cl.loadSubSamples()

else:
    cl.stride = cl.args.stride

    cl.loadM1()  
    ##cl.loadTethys()i ## not in this campaign
    cl.loadL_662a()
    cl.load_NPS34a() 
    cl.load_slocum_nemesis() 
    cl.load_wg_Tiny()
    cl.load_wg_Sparky()
    cl.load_oa1()
    cl.load_oa2()
    cl.loadDorado()
    cl.loadDaphne()
    cl.loadMakai()
    ##cl.loadRCuctd()  ## not in this campaign
    ##cl.loadRCpctd()  ## not in this campaign
    cl.loadWFuctd()
    cl.loadWFpctd()

    #cl.loadSubSamples() ## no subSamples yet...

# Add any X3D Terrain information specified in the constructor to the database - must be done after a load is executed
cl.addTerrainResources()

print "All Done."
