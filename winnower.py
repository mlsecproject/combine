#! /usr/bin/env python
import csv
import json
import pygeoip

from netaddr import IPAddress, IPRange, IPSet

def load_gi_org(filename):
    gi_org = {}
    with open(filename, 'rb') as f:
        org_reader = csv.DictReader(f, fieldnames=['start', 'end', 'org'])
        for row in org_reader:
            gi_org[row['org']] = IPRange(row['start'], row['end'])
    return gi_org


def maxmind(address):
    pass


def maxhits(dns_records):
    pass


def dnsdb(address, record_type):
    pass


def enrich_IPv4(address):
    as_num, as_name, country = maxmind(address)
    hostname = maxhits(dnsdb(address, "PTR"))
    return (address, as_num, as_name, country, hostname)


def reserved(address):
    # from http://en.wikipedia.org/wiki/Reserved_IP_addresses:
    ranges = IPSet(['0.0.0.0/8', '100.64.0.0/10', '127.0.0.0/8', '192.88.99.0/24', 
                    '198.18.0.0/15', '198.51.100.0/24', '203.0.113.0/24', '233.252.0.0/24'])
    a_reserved = address.is_reserved()
    a_private = address.is_private()
    a_inr = address in ranges
    if a_reserved or a_private or a_inr:
        return True
    else:
        return False


def winnow(in_file, out_file, enr_file):
    with open(in_file, 'rb') as f:
        crop = json.load(f)

    org_data = load_gi_org('data/GeoIPASNum2.csv')
    #country_data = load_gi_country('data/')

    wheat = []
    enriched = []

    for each in crop:
        (addr, addr_type, direction, source, note, date) = each
        if addr_type == 'IPv4':
            ipaddr = IPAddress(addr)
            if not reserved(ipaddr):
                wheat.append(each)
                #enriched.append(enrich_IPv4(ipaddr))
            else:
                print "%s is reserved, sorry" % addr


    with open(out_file, 'wb') as f:
        json.dump(wheat, f, indent=2)

    #with open(enr_file, 'wb') as f:
        #json.dump(enriched, f, indent=2)


if __name__ == "__main__":
    winnow('crop.json', 'wheat.json', 'enriched.json')
