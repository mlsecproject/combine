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

The output can optionally be filtered and enriched with additional data. The enrichments look like the following:<br/>
(url, domain, and ip have been added as additional fields if they're present in the original feed)
```
"entity","type","direction","source","notes","date","url","domain","ip","asnumber","asname","country","hostname","ips","mx"
"gmail.com","FQDN","outbound","nothink","","2015-02-13","","","","","","","","173.194.37.54|173.194.37.53","alt3.gmail-smtp-in.l.google.com.|alt4.gmail-smtp-in.l.google.com.|alt1.gmail-smtp-in.l.google.com.|alt2.gmail-smtp-in.l.google.com.|gmail-smtp-in.l.google.com."
"google.com","FQDN","outbound","nothink","","2015-02-13","","","","","","","","74.125.196.113|74.125.196.100|74.125.196.101|74.125.196.138|74.125.196.102|74.125.196.139","aspmx.l.google.com.|alt3.aspmx.l.google.com.|alt2.aspmx.l.google.com.|alt4.aspmx.l.google.com.|alt1.aspmx.l.google.com."
"146.185.246.96","IPv4","outbound","nothink","","2015-02-13","","","","201781","Unikalnie Technologii ltd.","RU","","",""
"173.45.105.218","IPv4","outbound","nothink","","2015-02-13","","","","10297","eNET Inc.","US","","",""
"173.45.106.170","IPv4","outbound","nothink","","2015-02-13","","","","10297","eNET Inc.","US","","",""
"193.106.175.180","IPv4","outbound","nothink","","2015-02-13","","","","50465","IQHost Ltd","RU","","",""
"91.236.74.164","IPv4","inbound","nothink","","2015-02-13","","","","198540","Przedsiebiorstwo Uslug Specjalistycznych ELAN mgr inz. Andrzej Niechcial","PL","","",""
"116.255.215.240","IPv4","inbound","openbl","","2015-02-13","","","","37943","ZhengZhou GIANT Computer Network Technology Co., Ltd","CN","","",""
```

The enrichments include:
* AS Name and Number information gathered from [MaxMind GeoIP ASN Database](http://dev.maxmind.com/geoip/legacy/geolite/)
* Country Code information gathered from [MaxMind GeoIP Database](http://dev.maxmind.com/geoip/legacy/geolite/)
* Host resolution and Reverse Host information is gathered from [Farsight Security's DNSDB](https://api.dnsdb.info/)
* PTR DNS lookup - non-Farsight
* A DNS lookup - non-Farsight
* MX DNS lookup - non-Farsight

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

To use some of the plugins you should also grab [uniaccept-python](https://github.com/icann/uniaccept-python), and install it.

At this point you should be ready to run Combine.

We also have a [dockerfile](https://github.com/mlsecproject/combine/tree/master/docker) available *Non-Plugin version*.

*Note, there is an issue running this under Python 2.7.9 that will cause all HTTPS URLs to fail*

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

### Creating a plugin

The plugin system uses yapsy, you will need a .py and a .yapsy-plugin file in the plugins directory in order for your plugin to be recognized.
To create a .yapsy-plugin file you need the following:

```
[Core]
Name = plugin name
Module = name of the .py file without the .py extension

[Documentation]   
Author = plugin author
Version = plugin version
Website = website for reference, yours or another one
Description = what the plugin does
```

Then create a .py file you can use this as a skeleton.

```
from yapsy.IPlugin import IPlugin

class PluginOne(IPlugin):
    NAME = name of the plugin from above
    DIRECTION = can be 'inbound', 'outbound', or 'file'
    URLS = ['a', 'list', 'of', 'urls']

    def get_URLs(self):
        return self.URLS

    def get_direction(self):
        return self.DIRECTION

    def get_name(self):
        return self.NAME

    def process_data(self, source, response)
        code you need to process the response (eg website text)
         this should return a list of dicts, look at some of the
         other plugins for examples
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
