#!/bin/bash
# This product includes GeoLite data created by MaxMind, available from http://www.maxmind.com

# you can set this up in the crontab to update it daily:
# 0 0 * * * [combine_folder]/data/update_maxmind.sh

wget -q http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz && gunzip -f GeoIP.dat.gz

wget -q http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz && gunzip -f GeoLiteCity.dat.gz
