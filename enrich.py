#! /usr/bin/env python


def enrich_IPv4(address):
    (ASN, AS_name, country) = maxmind(address)
    hostname = maxhits(dnsdb(each, "PTR"))
    return (address, ASN, AS_name, country, hostname)


def enrich_DNS(address):
    for ip_addr in dnsdb(address, "A")
        harvest += IPv4(ip_addr, host=FQDN.value)
        enrich(everyone)

        
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


