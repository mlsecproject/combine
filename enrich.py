# The following is ACTUALLY just pseudocode. Don't run this shit.

for each in IPv4_addresses:
    (ASN, AS_name, country) = maxmind(each)
    hostname = maxhits(dnsdb(each, "PTR"))
    each.enrichment = (ASN, AS_name, country, hostname)

for each in FQDN:
    for everyone in dnsdb(each, "A"):
        harvest += as.IPv4(everyone, host=FQDN.value)
        enrich(everyone)
