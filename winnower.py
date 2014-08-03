#! /usr/bin/env python
import ConfigParser
import csv
import dnsdb_query
import json
import pygeoip
import sys

from netaddr import IPAddress, IPRange, IPSet


def setup_dnsdb():
    config = ConfigParser.ConfigParser()
    config.read('combine.cfg')
    server = config.get('Winnower', 'dnsdb_server')
    api = config.get('Winnower', 'dnsdb_api')
    sys.stderr.write('Setting up DNSDB client\n')
    return dnsdb_query.DnsdbClient(server, api)


def load_gi_org(filename):
    gi_org = {}
    with open(filename, 'rb') as f:
        org_reader = csv.DictReader(f, fieldnames=['start', 'end', 'org'])
        for row in org_reader:
            gi_org[row['org']] = IPRange(row['start'], row['end'])
    return gi_org


def org_by_addr(address, org_data):
    as_num = None
    as_name = None
    for org in org_data:
        if address in org_data[org]:
            as_num, sep, as_name = org.partition(' ')
            break
    return as_num, as_name


def maxhits(dns_records):
    max = 0
    hostname = None
    for record in dns_records:
        if record['count'] > max:
            max = record['count']
            hostname = record['rrname'].rstrip('.')
    return hostname


def enrich_IPv4(address, org_data, geo_data, dnsdb):
    as_num, as_name = org_by_addr(address, org_data)
    country = geo_data.country_code_by_addr('%s' % address)
    hostname = maxhits(dnsdb.query_rdata_ip('%s' % address))
    if hostname:
        sys.stderr.write('Mapped %s to %s\n' % (address, hostname))

    return (as_num, as_name, country, None, hostname)


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

    # TODO: make these locations configurable?
    org_data = load_gi_org('data/GeoIPASNum2.csv')
    geo_data = pygeoip.GeoIP('data/GeoIP.dat')
    dnsdb = setup_dnsdb()

    wheat = []
    enriched = []

    for each in crop:
        (addr, addr_type, direction, source, note, date) = each
        # TODO: enrich DNS indicators as well
        if addr_type == 'IPv4':
            ipaddr = IPAddress(addr)
            if not reserved(ipaddr):
                wheat.append(each)
                # TODO: gracefully handle case of no DNSDB availability (other sources? cf. #38)
                e_data = (addr, addr_type, direction, source, note, date, enrich_IPv4(ipaddr, org_data, geo_data, dnsdb))
                enriched.append(enrich_IPv4(ipaddr, org_data, geo_data, dnsdb))
            else:
                sys.stderr.write("%s is reserved, sorry\n" % addr)
        # Notice that this means we filter out ALL non-IPv4 indicators

    with open(out_file, 'wb') as f:
        json.dump(wheat, f, indent=2)

    with open(enr_file, 'wb') as f:
        json.dump(enriched, f, indent=2)


if __name__ == "__main__":
    winnow('crop.json', 'crop.json', 'enriched.json')
