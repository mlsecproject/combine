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
from sortedcontainers import SortedDict

from logger import get_logger

logger = get_logger('winnower')

# from http://en.wikipedia.org/wiki/Reserved_IP_addresses:
reserved_ranges = IPSet(['0.0.0.0/8', '100.64.0.0/10', '127.0.0.0/8', '192.88.99.0/24',
                         '198.18.0.0/15', '198.51.100.0/24', '203.0.113.0/24', '233.252.0.0/24'])
gi_org = SortedDict()
geo_data = pygeoip.GeoIP('data/GeoIP.dat', pygeoip.MEMORY_CACHE)


def load_gi_org(filename):
    with open(filename, 'rb') as f:
        org_reader = csv.DictReader(f, fieldnames=['start', 'end', 'org'])
        for row in org_reader:
            gi_org[row['start']] = (IPRange(row['start'], row['end']), unicode(row['org'], errors='replace'))

    return gi_org


def org_by_addr(address):
    as_num = None
    as_name = None
    gi_index = gi_org.bisect(str(int(address)))
    gi_net = gi_org[gi_org.iloc[gi_index - 1]]
    if address in gi_net[0]:
        as_num, sep, as_name = gi_net[1].partition(' ')
        as_num = as_num.replace("AS", "")  # Making sure the variable only has the number
    return as_num, as_name


def maxhits(dns_records):
    hmax = 0
    hostname = None
    for record in dns_records:
        #logger.info("examining %s" % record)
        if record['count'] > hmax:
            hmax = record['count']
            hostname = record['rrname'].rstrip('.')
    return hostname


def maxhits_rdata(dns_records):
    hmax = 0
    hostname = None
    for record in dns_records:
        # logger.info("Examining %s" % record)
        if record['count'] > hmax:
            hmax = record['count']
            hostname = record['rdata'][0].rstrip('.')
    return hostname


def enrich_IPv4(address, dnsdb=None, hostname=None):
    as_num, as_name = org_by_addr(address)
    country = geo_data.country_code_by_addr('%s' % address)
    if dnsdb:
        inaddr = address.reverse_dns
        rhost = maxhits_rdata(dnsdb.query_rrset('%s' % inaddr))
    else:
        rhost = None
    return (as_num, as_name, country, hostname, rhost)


def enrich_FQDN(address, date, dnsdb):
    records = dnsdb.query_rrset(address, rrtype='A')
    yesterday = dt.datetime.strptime(date, '%Y-%m-%d') - dt.timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    records = filter_date(records, yesterday_str)
    enrichment = []
    if not records:
        return None
    for ip_addr in records[0]['rdata']:
        ip_addr_data = enrich_IPv4(IPAddress(ip_addr), dnsdb, address)
        enrichment.append((ip_addr,) + ip_addr_data)
    return enrichment


def filter_date(records, date):
    date_dt = dt.datetime.strptime(date, '%Y-%m-%d')
    start_dt = dt.datetime.combine(date_dt, dt.time.min).strftime('%Y-%m-%d %H:%M:%S')
    end_dt = dt.datetime.combine(date_dt, dt.time.max).strftime('%Y-%m-%d %H:%M:%S')
    return dnsdb_query.filter_before(dnsdb_query.filter_after(records, start_dt), end_dt)


def reserved(address):
    a_reserved = address.is_reserved()
    a_private = address.is_private()
    a_inr = address in reserved_ranges
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
    if enrich_ip == '1' or enrich_ip == 'True':
        enrich_ip = True
        logger.info('Enriching IPv4 indicators: TRUE')
    else:
        enrich_ip = False
        logger.info('Enriching IPv4 indicators: FALSE')

    enrich_dns = config.get('Winnower', 'enrich_dns')
    if enrich_dns == '1' or enrich_dns == 'True':
        enrich_dns = True
        logger.info('Enriching DNS indicators: TRUE')
    else:
        enrich_dns = False
        logger.info('Enriching DNS indicators: FALSE')

    logger.info('Setting up DNSDB client')

    # handle the case where we aren't using DNSDB
    dnsdb = dnsdb_query.DnsdbClient(server, api)
    if api == 'YOUR_API_KEY_HERE' or len(dnsdb.query_rdata_name('google.com')) == 0:
        dnsdb = None
        logger.info('Invalid DNSDB configuration found')

    with open(in_file, 'rb') as f:
        crop = json.load(f)

    # TODO: make these locations configurable?
    logger.info('Loading GeoIP data')
    gi_org = load_gi_org('data/GeoIPASNum2.csv')

    wheat = []
    enriched = []

    logger.info('Beginning winnowing process')
    for each in crop:
        (addr, addr_type, direction, source, note, date) = each
        # this should be refactored into appropriate functions
        if addr_type == 'IPv4' and is_ipv4(addr):
            #logger.info('Enriching %s' % addr)
            ipaddr = IPAddress(addr)
            if not reserved(ipaddr):
                wheat.append(each)
                if enrich_ip:
                    e_data = (addr, addr_type, direction, source, note, date) + enrich_IPv4(ipaddr, dnsdb)
                    enriched.append(e_data)
                else:
                    e_data = (addr, addr_type, direction, source, note, date) + enrich_IPv4(ipaddr)
                    enriched.append(e_data)
            else:
                logger.error('Found invalid address: %s from: %s' % (addr, source))
        elif addr_type == 'FQDN' and is_fqdn(addr):
            #logger.info('Enriching %s' % addr)
            wheat.append(each)
            if enrich_dns and dnsdb:
                # print "Enriching %s" % addr
                e_data = enrich_FQDN(addr, date, dnsdb)
                if e_data:
                    for each in e_data:
                        datum = (each[0], "IPv4", direction, source, note, date) + each[1:]
                        enriched.append(datum)
        else:
            logger.error('Could not determine address type for %s listed as %s' % (addr, addr_type))

    logger.info('Dumping results')
    with open(out_file, 'wb') as f:
        w_data = json.dumps(wheat, indent=2, ensure_ascii=False).encode('utf8')
        f.write(w_data)

    with open(enr_file, 'wb') as f:
        e_data = json.dumps(enriched, indent=2, ensure_ascii=False).encode('utf8')
        f.write(e_data)


if __name__ == "__main__":
    winnow('crop.json', 'crop.json', 'enriched.json')
