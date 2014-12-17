#!/usr/bin/python
import json
import pygeoip

series={}
gi=pygeoip.GeoIP('../data/GeoLiteCity.dat')

flat_intel=[]

for ip in json.load(open('../crop.json','r')):
    skey=ip[3].split('/')[2]
    if not skey in series.keys():
        series[skey]=[]
    if ip[1]=="IPv4":
        geo=gi.record_by_addr(ip[0])
        if geo:    
            series[skey]+=[geo['latitude'],geo['longitude'],0.001]
	    here=False
	    for pres_intel in flat_intel:
		if pres_intel[0]==geo['latitude'] and pres_intel[1]==geo['longitude']:
		    pres_intel[2]+=0.0001
		    here=True
		    break
	    if not here:
		flat_intel.append([geo['latitude'],geo['longitude'],0.0001])

outjson=[]
for fi in flat_intel:
    outjson+=fi

json.dump(outjson,open('intel.json','wb'))
