combine
=======

Combine gathers OSINT Threat Intelligence Feeds

You can run the original harvest.py tool with a cmd line like this:

````
python reaper.py 
python thresher.py
python baler.py
`````

The output will actually be a CSV with the following schema:
```
entity, datatype, direction, source, notes, date
```
- The `entity` field consists of a FQDN or IPv4 address (supported entities at the moment)
- The `datatype` field consists of either `FQDN` or `IPv4`, classifying the type of the entity
- The `direction` field will be either `inbound` or `outbound`
- The `source` field contains the original URL.
- The `notes` field should cover any extra tag info we may want to persist with the data
- The `date` field will be in `YYYY-MM-DD` format.
- All fields are quoted with double-quotes (`"`).

An output example:
```
"entity","type","direction","source","notes","date"
"24.210.174.91","IPv4","inbound","openbl","SSHscan","2014-06-01"
"201.216.191.174","IPv4","inbound","openbl","SSHscan","2014-06-01"
"114.130.9.21","IPv4","inbound","openbl","FTPscan","2014-06-01"
"175.45.187.30","IPv4","inbound","openbl","SSHscan","2014-06-01"
"118.69.201.55","IPv4","inbound","openbl","SSHscan","2014-06-01"
"citi-bank.ru","FQDN","outbound","mtc_malwaredns","Malware","2014-06-01"
"ilo.brenz.pl","FQDN","outbound","mtc_malwaredns","Malware","2014-06-01"
"utenti.lycos.it","FQDN","outbound","mtc_malwaredns","Malware","2014-06-01"
"bgr.runk.pl","FQDN","outbound","mtc_malwaredns","Malware","2014-06-01"
```

The output can optionally be filtered and enriched with additional data. The enrichments look like the following:
```
"entity","type","direction","source","notes","date","asnumber","asname","country","host","rhost"
"1.234.23.28","IPv4","outbound","alienvault","MLSec-Export","2014-04-03","9318","Hanaro Telecom Inc.","KR",,
"1.234.35.198","IPv4","outbound","alienvault","MLSec-Export","2014-04-03","9318","Hanaro Telecom Inc.","KR",,
"1.25.36.76","IPv4","outbound","alienvault","MLSec-Export","2014-04-03","4837","CNCGROUP China169 Backbone","CN",,
"1.93.1.162","IPv4","outbound","alienvault","MLSec-Export","2014-04-03","4808","CNCGROUP IP network China169 Beijing Province Network","CN",,
"1.93.44.147","IPv4","outbound","alienvault","MLSec-Export","2014-04-03","4808","CNCGROUP IP network China169 Beijing Province Network","CN",,
"100.42.218.250","IPv4","outbound","alienvault","MLSec-Export","2014-04-03","18450","WebNX, Inc.","US",,"100-42-218-250.static.webnx.com"
"100.42.55.2","IPv4","outbound","alienvault","MLSec-Export","2014-04-03","36351","SoftLayer Technologies Inc.","US",,"stats.wren.arvixe.com"
"100.42.55.220","IPv4","outbound","alienvault","MLSec-Export","2014-04-03","36351","SoftLayer Technologies Inc.","US",,"stats.warthog.arvixe.com"
"100.42.58.137","IPv4","outbound","alienvault","MLSec-Export","2014-04-03","36351","SoftLayer Technologies Inc.","US",,"100.42.58.137-static.reverse.mysitehosted.com"
```

### Copyright Info

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

Copyright 2014 MLSec Project

Licensed under GPLv3 - https://github.com/mlsecproject/combine/blob/master/LICENSE
