#!/usr/bin/env python

"""
More elaborate example trying to retrieve as much data as possible from a
Trimble Copernicus II GPS. It shows how to
a) Establish a connection to the GPS.
b) Send request packets to the GPS.
c) Read report packets from the GPS and extract data.
Includes code inspired and co-written by Daniel Macia.
"""

import tsip
import serial
import threading
import sys
import numpy
from numpy import *
from datetime import datetime
import datetime
import os

SERIAL = '/dev/ttyS0'
BAUD = 9600


def getlatlogn():
    #print('IN LAT LONG')
    i = 1
    gps_conn.write(tsip.Packet(0x35, 0, 0, 0, 0))
    while(i == 1):
        gps_conn.write(tsip.Packet(0x35, 0, 0, 0, 0))
        report_latitude_rd        = gps_conn.read()
        if(report_latitude_rd[0] == 143 and len(report_latitude_rd) >= 5):
             try:
                 lat                           = report_latitude_rd[17]#In radians #*180*2**31/(180*pi)   #In semicircles
                 logn                          = report_latitude_rd[18]#In radians#*180*2**31)/(180*pi) #In semicircles
                 i = 0
                        #print("TRYING")
             except:
                 pass;
        #print('STUCK IN LOOP')
    return lat, logn

def getelevation():
    i = 1
    while(i ==1):
        gps_conn.write(tsip.Packet(0x3C, 0)) # Changed 0 to 1, to have consitant IPP# 0 is to denote all satellite incurrent tracking set.    
        # Request Signal Levels
        report_elevation_angle_rd = gps_conn.read()
        if(report_elevation_angle_rd[0] == 92):
             try:
                 elevation       =       report_elevation_angle_rd[7]#In radians#*180*2**31/(180*pi) #In semicircles 
                 azimuth_angle   =       report_elevation_angle_rd[8]#In radians#*180*2**31/(180*pi) #In semicircles 
                 i              =       0
             except:
                 pass;
    return elevation, azimuth_angle

def getgpstime():
    i = 1
    while(i == 1):
        gps_conn.write(tsip.Packet(0x8E,0xAC, 2))
        report_time         =       gps_conn.read()
        #print(report_time)
        if(report_time[0] == 143 and len(report_time) < 14):
            try:
                 gps_time1                          = report_time[2]
                 i                                = 0
#                       return gps_time
            except:
                 pass;
    return gps_time1
def getion():
    i   =       1
    a = zeros((4))
    b = zeros((4))
    while(i == 1):
          gps_conn.write(tsip.Packet(0x38, 1, 4, 0))#Changed from 0 to 1, stellite view..
          report_iono         =       gps_conn.read()
          if(report_iono[0] == 88):
               try:
                    a[0]                        = report_iono[5]
                    a[1]                            = report_iono[6]
                    a[2]                            = report_iono[7]
                    a[3]                            = report_iono[8]

                    b[0]                          = report_iono[9]
                    b[1]                          = report_iono[10]
                    b[2]                          = report_iono[11]
                    b[3]                          = report_iono[12]

                    i                                 = 0
#                               return gps_time
               except:
                    pass;
    return a, b

# The WRITE flag indicates to the main loop when to send
# request packets to the GPS. It is set in the `set_write_flag()`
# function which is called through a `threading.Timer()`. 
#
WRITE = True
WRITE_INTERVAL = 5

def set_write_flag():
    global WRITE
    WRITE = 1
def cal_TEC(elevation, azimuth_angle, fopen, fopen2):
    gps_time                    = getgpstime()#+5.5*60*60

    AMP         = 0#zeros((4))
    PER         = 0#zeros((4))
    sih         = 0.0137/(elevation*rad2semi + 0.11)-0.022
    F           = 1.0+16.0*(0.53-elevation*rad2semi)**3

    phii        = lat*rad2semi+sih*cos(azimuth_angle)
    if(phii>0.416):
        print('\n\n\n')
        phii    =       0.416
    if(phii<-0.416):
        print('\n\n\n')
        phhi    =       -0.416
    lami        = logn*rad2semi+sih*sin(azimuth_angle)/cos(phii/rad2semi)
    phim        = float(phii) + 0.064*cos((lami-1.617)/rad2semi)
    a, b        = getion()
    t           = 43200*float(lami) + gps_time
    t           = t%86400
    AMP = a[0]+a[1]*phim+a[2]*phim**2+a[3]*phim**3
    PER = b[0]+b[1]*phim+b[2]*phim**2+b[3]*phim**3
    if(AMP < 0):
        AMP = 0
    if(PER < 72000.00):
        PER = 72000.00
    x = 2*pi*(t-50400.00)/PER

    if(x>-1.57 and x<1.57):
        Tiono   =       F*5*10**-9+F*AMP*(1-x**2/2+x**4/24.00)
        print("In forst condition")
    else:
        Tiono   =       F*5*10**-9
    print('Delay due to Ionosphere: '+str(Tiono))
    TEC = Tiono*3*10**8*1.57542**2*10**18/(2*40.3)
    print('Total Electron Content : '+str(TEC))
    print('phim                   = '+str(phim))
    print('phii                   = '+str(phii))
    print('x                      = '+str(x))
    print('t                      = '+str(t))
    print('Elevation              = '+str(elevation*180/pi))
    print('Azimuth                = '+str(azimuth_angle*180/pi))
    print(' lat*rad2semi, sih*cos(azimuth_angle)')
    print( lat*rad2semi, sih*cos(azimuth_angle))
    TEC = Tiono*3*10**8*1.57542**2*10**18/(2*40.3)
    ar  = array([gps_time, Tiono, TEC, phim, phii, lami, PER, AMP, sih, lat*180/pi, logn*180/pi, elevation*180/pi, azimuth_angle*180/pi, x, t])
    ar1 = array([gps_time, a, b, TEC, elevation*180/pi, azimuth_angle*180/pi])
    savetxt(fopen, ar[None], fmt='%s')
    fopen.write('\n')
    savetxt(fopen2, ar1[None], fmt='%s')
    fopen2.write('\n')
    fopen.close()
    fopen2.close()
    os.system('sleep 0.5s')

def write_init_file():
    #Opening TEC REC file
    REC_fil         = 'TEC_REC_date_'+str(datetime.datetime.now().day)+'_'+str(datetime.datetime.now().month)+'_'+str(datetime.datetime.now().year)
    fopen           = open(REC_fil, 'a')
    fopen.write('#GPS Time of the week (sec)\tDelay due to Ionosphere (sec)\tTEC (electrons/m**2)\tphim (semicircles)\tphii (semicircles)\tlami (semicircles)\tPER\tAMP\tsih\tlat\tlogn\televation\tazimuth\tx\tt\n')


    #Opening alpha beta file..
    TEC_a_b          = 'TEC_alpha_beta'+str(datetime.datetime.now().day)+'_'+str(datetime.datetime.now().month)+'_'+str(datetime.datetime.now().year)
    fopen2           = open(TEC_a_b, 'a')
    fopen2.write("#alpha\tbeta\tTEC\televation(deg.)\tazimuth_angle(deg.)")
    return REC_fil, TEC_a_b

def write_conti_file(REC_fil_init, TEC_a_b_inti):
    #Opening TEC REC file
    REC_fil         = 'TEC_REC_date_'+str(datetime.datetime.now().day)+'_'+str(datetime.datetime.now().month)+'_'+str(datetime.datetime.now().year)
    fopen           = open(REC_fil, 'a')


    #Opening alpha beta file..
    TEC_a_b          = 'TEC_alpha_beta'+str(datetime.datetime.now().day)+'_'+str(datetime.datetime.now().month)+'_'+str(datetime.datetime.now().year)
    fopen2           = open(TEC_a_b, 'a')
    if(REC_fil_init != REC_fil):
        fopen.write('#GPS Time of the week (sec)\tDelay due to Ionosphere (sec)\tTEC (electrons/m**2)\tphim (semicircles)\tphii (semicircles)\tlami (semicircles)\tPER\tAMP\tsih\tlat\tlogn\televation\tazimuth\tx\tt\n')
        #Updating the initial file name..
        REC_fil_init= 'TEC_REC_date_'+str(datetime.datetime.now().day)+'_'+str(datetime.datetime.now().month)+'_'+str(datetime.datetime.now().year)
    if(TEC_a_b_inti != TEC_a_b):
        fopen2.write("#alpha\tbeta\tTEC\televation(deg.)\tazimuth_angle(deg.)")
        TEC_a_b_inti = 'TEC_alpha_beta'+str(datetime.datetime.now().day)+'_'+str(datetime.datetime.now().month)+'_'+str(datetime.datetime.now().year)
    return fopen, fopen2

timer = threading.Timer(WRITE_INTERVAL, set_write_flag)
timer.start()


# Open serial connection to Copernicus II receiver
serial_conn     = serial.Serial(SERIAL, BAUD)
gps_conn        = tsip.GPS(serial_conn)

rad2semi        =       1/pi
semi2rad        =       1/rad2semi

lat, logn                   = getlatlogn()
print('Current lat long..')
print(lat*180/pi, logn*180/pi)
#Writing inital file..
REC_fil_init, TEC_a_b_inti               =  write_init_file()


while True:
    if(int(datetime.datetime.now().hour) == int(0) and int(datetime.datetime.now().minute) == int(1)):
        #Running plotting routine..
        os.system('python plot_TEC.py')
    fopen, fopen2       =        write_conti_file(REC_fil_init, TEC_a_b_inti)
    print('Getting Elevation angle between user and satellite, ref. IS-GPS-200D, pg.125, fig. 20-4, Ionospheric Model')
    elevation, azimuth_angle    = getelevation()
    if(elevation>30*pi/180.0):
        cal_TEC(elevation, azimuth_angle, fopen, fopen2)
