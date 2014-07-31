#! /usr/bin/env python


def maxmind(address):
    pass


def maxhits(dns_records):
    pass


def dnsdb(address, record_type):
    pass


def enrich_IPv4(address):
    (ASN, AS_name, country) = maxmind(address)
    hostname = maxhits(dnsdb(each, "PTR"))
    return (address, ASN, AS_name, country, hostname)


# honestly this bit can wait since we're not processing DNS right now
def enrich_DNS(address):
    for ip_addr in dnsdb(address, "A"):
        # how do we add this back?
        harvest += IPv4(ip_addr, host=FQDN.value)
        # and return this?
        enrich_IPv4(ip_addr)


def enrich(data):
    enrichment = []
    for indicator in data:
        if indicator_type(indicator) == 'IPv4':
            enrichment.append(enrich_IPv4(indicator))
        elif indicator_type(indicator) == 'DNS':
            enrichment.append(enrich_DNS(indicator))
        else:
            print "Can't determine type: %s" % indicator
    return enrichment


def reserved(address):
    # from http://en.wikipedia.org/wiki/Reserved_IP_addresses:
    ranges = ['0.0.0.0/8',
              '10.0.0.0/8',
              '100.64.0.0/10',
              '127.0.0.0/8',
              '169.254.0.0/16',
              '172.16.0.0/12',
              '192.0.0.0/29',
              '192.0.2.0/24',
              '192.88.99.0/24',
              '192.168.0.0/16',
              '198.18.0.0/15',
              '198.51.100.0/24',
              '203.0.113.0/24',
              '224.0.0.0/4',
              '233.252.0.0/24',
              '240.0.0.0/4',
              '255.255.255.254/32']


def filter(data):
    harvest = []
    for address in data:
        if indicator_type(address) == IPv4:
            # this step is because of shitty SANS data
            ip_addr = ip_normalize(address)
            if not reserved(ip_addr):
                harvest.append(ip_addr)
