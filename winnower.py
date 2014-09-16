#! /usr/bin/env python
import ConfigParser
import csv
import datetime as dt
import dnsdb_query
import json
import pygeoip
import sys

from netaddr import IPAddress, IPRange, IPSet


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


def enrich_IPv4(address, org_data, geo_data, dnsdb=None):
    as_num, as_name = org_by_addr(address, org_data)
    country = geo_data.country_code_by_addr('%s' % address)
    if dnsdb:
        hostname = maxhits(dnsdb.query_rdata_ip('%s' % address))
    else:
        hostname = None
    return (as_num, as_name, country, None, hostname)


def enrich_FQDN(address, date, dnsdb):
    records = dnsdb.query_rrset(address, rrtype='A')
    records = filter_date(records, date)
    ip_addr = maxhits(records)
    if ip_addr:
        sys.stderr.write('Mapped %s to %s\n' % (address, ip_addr))
    return ip_addr


def filter_date(records, date):
    date_dt = dt.datetime.strptime(date, '%Y-%m-%d')
    start_dt = dt.datetime.combine(date_dt, dt.time.min).strftime('%Y-%m-%d %H:%M:%S')
    end_dt = dt.datetime.combine(date_dt, dt.time.max).strftime('%Y-%m-%d %H:%M:%S')
    return dnsdb_query.filter_before(dnsdb_query.filter_after(records, start_dt), end_dt)


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
    config = ConfigParser.SafeConfigParser(allow_no_value=True)
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        sys.stderr.write('Could not read combine.cfg.\n')
        sys.stderr.write('HINT: edit combine-example.cfg and save as combine.cfg.\n')
        return

    server = config.get('Winnower', 'dnsdb_server')
    api = config.get('Winnower', 'dnsdb_api')
    enrich_ip = config.get('Winnower', 'enrich_ip')
    if enrich_ip == '1':
        enrich_ip = True
        sys.stderr.write('Enriching IPv4 indicators: TRUE\n')
    else:
        enrich_ip = False
        sys.stderr.write('Enriching IPv4 indicators: FALSE\n')

    enrich_dns = config.get('Winnower', 'enrich_dns')
    if enrich_dns == '1':
        enrich_dns = True
        sys.stderr.write('Enriching DNS indicators: TRUE\n')
    else:
        enrich_dns = False
        sys.stderr.write('Enriching DNS indicators: FALSE\n')

    sys.stderr.write('Setting up DNSDB client\n')
    dnsdb = dnsdb_query.DnsdbClient(server, api)

    with open(in_file, 'rb') as f:
        crop = json.load(f)

    # TODO: make these locations configurable?
    sys.stderr.write('Loading GeoIP data\n')
    org_data = load_gi_org('data/GeoIPASNum2.csv')
    geo_data = pygeoip.GeoIP('data/GeoIP.dat')

    wheat = []
    enriched = []

    sys.stderr.write('Beginning winnowing process\n')
    for each in crop:
        (addr, addr_type, direction, source, note, date) = each
        # TODO: enrich DNS indicators as well
        if addr_type == 'IPv4':
            sys.stderr.write('Enriching %s\n' % addr)
            ipaddr = IPAddress(addr)
            if not reserved(ipaddr):
                wheat.append(each)
                if enrich_ip:
                    e_data = (addr, addr_type, direction, source, note, date, enrich_IPv4(ipaddr, org_data, geo_data, dnsdb))
                    enriched.append(e_data)
                else:
                    e_data = (addr, addr_type, direction, source, note, date, enrich_IPv4(ipaddr, org_data, geo_data))
                    enriched.append(e_data)
            else:
                sys.stderr.write('Found invalid address: %s from: %s\n' % (addr, source))
        elif addr_type == 'FQDN':
            # TODO: validate these (cf. https://github.com/mlsecproject/combine/issues/15 )
            sys.stderr.write('Enriching %s\n' % addr)
            wheat.append(each)
            if enrich_dns:
                e_data = (addr, addr_type, direction, source, note, date, enrich_FQDN(ipaddr, date, dnsdb))
                enriched.append(e_data)

    sys.stderr.write('Dumping results\n')
    with open(out_file, 'wb') as f:
        json.dump(wheat, f, indent=2)

    with open(enr_file, 'wb') as f:
        json.dump(enriched, f, indent=2)


if __name__ == "__main__":
    winnow('crop.json', 'crop.json', 'enriched.json')
