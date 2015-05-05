[![Stories in Ready](https://badge.waffle.io/mlsecproject/combine.png?label=ready&title=Ready)](https://waffle.io/mlsecproject/combine)
[![Stories in In Progress](https://badge.waffle.io/mlsecproject/combine.png?label=in%20progress&title=In%20Progress)](https://waffle.io/mlsecproject/combine)
Combine
=======

Combine gathers Threat Intelligence Feeds from publicly available sources

You can run the core tool with `combine.py`:
```
usage: combine.py [-h] [-t TYPE] [-f FILE] [-d] [-e] [--tiq-test]

optional arguments:
  -h, --help            show this help message and exit
  -t TYPE, --type TYPE  Specify output type. Currently supported: CSV and exporting to CRITs
  -f FILE, --file FILE  Specify output file. Defaults to harvest.FILETYPE
  -d, --delete          Delete intermediate files
  -e, --enrich          Enrich data
  --tiq-test            Output in tiq-test format (implies -e)
```

Alternately, you can run each phase individually:


````
python reaper.py
python thresher.py
python winnower.py
python baler.py
````

The output will actually be a CSV with the following schema:
```
entity, type, direction, source, notes, date
```
- The `entity` field consists of a FQDN or IPv4 address (supported entities at the moment)
- The `type` field consists of either `FQDN` or `IPv4`, classifying the type of the entity
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

The enrichments include:
* AS Name and Number information gathered from [MaxMind GeoIP ASN Database](http://dev.maxmind.com/geoip/legacy/geolite/)
* Country Code information gathered from [MaxMind GeoIP Database](http://dev.maxmind.com/geoip/legacy/geolite/)
* Host resolution and Reverse Host information is gathered from [Farsight Security's DNSDB](https://api.dnsdb.info/)

In order to use the DNSDB's information you will require an API key from Farsight Security to use the enrichment.
If you do not have one, you can request one [here](https://www.dnsdb.info/#Apply).

You should configure the API key and endpoint for DNSDB on `combine.cfg`. Copy the example configuration file from `combine-example.cfg` and add your information there.

### Installation

Installation on Unix and Unix-like systems is straightforward. Either clone the repository or download the [latest release](https://github.com/mlsecproject/combine/releases). You will need pip and the python development libraries. In Ubuntu, the following commands will get you prepared:

```
sudo apt-get install python-dev python-pip python-virtualenv git
git clone https://github.com/mlsecproject/combine.git
cd combine
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

At this point you should be ready to run Combine.

We also have a [dockerfile](https://github.com/mlsecproject/combine/tree/master/docker) available.


### Exporting to CRITs

In order to use the [CRITs](https://crits.github.io/) exporting function, there are some configuration that is
necessary on the Baler section of the configuration file. Make sure you configure the following entries correctly:

```
crits_url = http://crits_url:crits_port/api/v1/
crits_username = CRITS_USERNAME
crits_api_key = CRITS_API_KEY
crits_campaign = combine
crits_maxThreads = 10
```
Make sure you have the campaign created on CRITs before exporting the data. The `confidence` field is being
set as `medium` throughout the export by default.

Thanks to [@paulpc](https://github.com/paulpc) for implementing this feature and [@mgoffin](https://github.com/mgoffin) for moral support ;).

### Copyright Info

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

Copyright (c) 2014-2015 MLSec Project

Licensed under GPLv3 - https://github.com/mlsecproject/combine/blob/master/LICENSE

### DNSDB used under Apache license

Copyright (c) 2013 by Farsight Security, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

### MaxMind GeoIP Databases used under CC licence

This product includes GeoLite data created by MaxMind, available from
[http://www.maxmind.com](http://www.maxmind.com).
