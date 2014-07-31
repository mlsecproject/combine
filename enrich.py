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
    for ip_addr in dnsdb(address, "A")
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
