#!/bin/bash
echo "This product includes GeoLite data created by MaxMind, available from http://www.maxmind.com"

wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz && gunzip -f GeoIP.dat.gz

wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz && gunzip -f GeoLiteCity.dat.gz