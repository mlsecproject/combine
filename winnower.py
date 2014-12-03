#! /usr/bin/env python
import ConfigParser
import csv
import datetime as dt
import dnsdb_query
import json
import pygeoip
import re
import sys

from netaddr import IPAddress, IPRange, IPSet

from logger import get_logger
import logging

logger = get_logger('winnower')


def load_gi_org(filename):
    gi_org = {}
    with open(filename, 'rb') as f:
        org_reader = csv.DictReader(f, fieldnames=['start', 'end', 'org'])
        for row in org_reader:
            gi_org[IPRange(row['start'], row['end'])] = row['org']
    return gi_org


def org_by_addr(address, org_data):
    as_num = None
    as_name = None
    for iprange in org_data:
        if address in iprange:
            as_num, sep, as_name = org_data[iprange].partition(' ')
            as_num = as_num.replace("AS", "")  # Making sure the variable only has the number
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
        logger.info('Mapped %s to %s' % (address, ip_addr))
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


def is_ipv4(address):
    if re.match('(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', address):
        return True
    else:
        return False


def is_fqdn(address):
    if re.match('(?=^.{4,255}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}$)', address):
        return True
    else:
        return False


def winnow(in_file, out_file, enr_file):
    config = ConfigParser.SafeConfigParser(allow_no_value=True)
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        logger.error('Winnower: Could not read combine.cfg.')
        logger.error('HINT: edit combine-example.cfg and save as combine.cfg.')
        return

    server = config.get('Winnower', 'dnsdb_server')
    api = config.get('Winnower', 'dnsdb_api')
    enrich_ip = config.get('Winnower', 'enrich_ip')
    if enrich_ip == '1':
        enrich_ip = True
        logger.info('Enriching IPv4 indicators: TRUE')
    else:
        enrich_ip = False
        logger.info('Enriching IPv4 indicators: FALSE')

    enrich_dns = config.get('Winnower', 'enrich_dns')
    if enrich_dns == '1':
        enrich_dns = True
        logger.info('Enriching DNS indicators: TRUE')
    else:
        enrich_dns = False
        logger.info('Enriching DNS indicators: FALSE')

    logger.info('Setting up DNSDB client')
    dnsdb = dnsdb_query.DnsdbClient(server, api)

    with open(in_file, 'rb') as f:
        crop = json.load(f)

    # TODO: make these locations configurable?
    logger.info('Loading GeoIP data')
    org_data = load_gi_org('data/GeoIPASNum2.csv')
    geo_data = pygeoip.GeoIP('data/GeoIP.dat', pygeoip.MEMORY_CACHE)

    wheat = []
    enriched = []

    logger.info('Beginning winnowing process')
    for each in crop:
        (addr, addr_type, direction, source, note, date) = each
        # TODO: enrich DNS indicators as well
        if addr_type == 'IPv4' and is_ipv4(addr):
            logger.info('Enriching %s' % addr)
            ipaddr = IPAddress(addr)
            if not reserved(ipaddr):
                wheat.append(each)
                if enrich_ip:
                    e_data = (addr, addr_type, direction, source, note, date) + enrich_IPv4(ipaddr, org_data, geo_data, dnsdb)
                    enriched.append(e_data)
                else:
                    e_data = (addr, addr_type, direction, source, note, date) + enrich_IPv4(ipaddr, org_data, geo_data)
                    enriched.append(e_data)
            else:
                logger.error('Found invalid address: %s from: %s' % (addr, source))
        elif addr_type == 'FQDN' and is_fqdn(addr):
            # TODO: validate these (cf. https://github.com/mlsecproject/combine/issues/15 )
            logger.info('Enriching %s' % addr)
            wheat.append(each)
            if enrich_dns:
                e_data = (addr, addr_type, direction, source, note, date, enrich_FQDN(addr, date, dnsdb))
                enriched.append(e_data)
        else:
            logger.error('Could not determine address type for %s listed as %s' % (addr, addr_type))

    logger.info('Dumping results')
    with open(out_file, 'wb') as f:
        json.dump(wheat, f, indent=2)

    with open(enr_file, 'wb') as f:
        json.dump(enriched, f, indent=2)


if __name__ == "__main__":
    winnow('crop.json', 'crop.json', 'enriched.json')
