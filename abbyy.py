
# coding: utf-8

import argparse
import csv
from colorama import Fore
import os
import requests
import sys
import time


# In[2]:

DLPATH = 'c:/users/michael/documents/txt files'

parser = argparse.ArgumentParser()

parser.add_argument('-l',help="Login- username:password",type=str)
parser.add_argument('-f',help="Forward - number to forward to",type=str)
parser.add_argument('-v',help="display progress info",action="store_true")

args = parser.parse_args()

# In[3]:



def process_file(file):
    try:
        rtxt = ' '.join(open(os.path.join(DLPATH,file),'r',encoding='utf-16').readlines())
    except:
        rtxt = ' '.join(open(os.path.join(DLPATH,file),'r',encoding='utf-8').readlines())
        
    prev = lat = lon = 0
    
    for l,line in enumerate(rtxt.split('\n')):
        if 'latitude' in line.lower():
            
            lat = (line.lower().replace(':','').split('latitude')[-1].strip())
            
            ### The following 'if' statements are patches for special cases ###
            if 'longitude' in lat:
                lat,lon = lat.split('longitude')
            if 'acres' in lat:
                lat = lat.split('acres')[-1].strip()
            if '    ' in lat:
                lat = lat.split('    ')[0].strip()
            ####################################################################
            break
            
    for l,line in enumerate(rtxt.split('\n')):
        if 'longitude' in line.lower():
            
            # lon may have already been set in one of the special cases above
            if lon == 0:
                lon = (line.lower().replace(':','').split('longitude')[-1].strip())
            ### The following 'if' statements are patches for special cases ###
            if '    ' in lon:
                lon = lon.split('    ')[0].strip()
            ###################################################################
            break
            
    for l,line in enumerate(rtxt.split('\n')):
        row = line.split()
        try:
            outrow = [float(x.replace(',','')) for x in row]
            if outrow:
                
                md,inc,azm,tvd,*_ = outrow
                
                yield [str(x) for x in (file.replace('.txt','.pdf'),md,inc,azm,tvd)] + [
                    lat.upper().replace('°',''),lon.upper().replace('°','')]
        except:
            pass


            
if __name__ == '__main__':
    files = [file for file in os.listdir(DLPATH)]

    header = "Original File,Measured Depth (MD),Inclination (Inc),Azimuth(Azi),Vertical Depth (TVD),Latitude,Longitude".split(',')

    with open('abbyy_results.csv','w',newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)
        retries = []
        for f,file in enumerate(files,start=1):
            done = int(50 * f / int(len(files)))
            sys.stdout.write("\r[%s%s] %s of %s files processed." % ('=' * done, ' ' * (50-done),f,len(files)))
            try:
                for outrow in process_file(file):
                    writeval = True
                    # Perform sanity check on output. No zeroes.
                    for x in outrow:
                        if x == '0' or x == '0.0':
                            writeval = False
                    if writeval:
                        writer.writerow(outrow)
            except:
                print(Fore.RED + "[-] error processing {}".format(file)
                retries.append(file)
