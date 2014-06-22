combine
=======

Combine gathers OSINT Threat Intelligence Feeds

You can run the original harvest.py tool with a cmd line like this:

````
./harvest.py -config harvest-outbound.cfg -output sample-output.txt
`````

The output will actually be a CSV with the following schema:
```
entity, type, direction, source, notes, date
```
- The `entity` field consists of a FQDN or IPv4 address (supported entities at the moment)
- The `type` field consists of either `FQDN` or `IPv4`, classifying the type of the entity
- The `direction` field will be either `inbound` or `outbound`
- The `notes` field should cover any extra tag info we may want to persist with the data
- The `date` field will be in `YYYY-MM-DD` format.

An output example:
```
entity, type, direction, source, notes, date
24.210.174.91,IPv4,inbound,openbl,SSH scan,2014-06-01
201.216.191.174,IPv4,inbound,openbl,SSH scan,2014-06-01
114.130.9.21,IPv4,inbound,openbl,FTP scan,2014-06-01
175.45.187.30,IPv4,inbound,openbl,SSH scan,2014-06-01
118.69.201.55,IPv4,inbound,openbl,SSH scan,2014-06-01
citi-bank.ru,FQDN,outbound,mtc_malwaredns,Malware,2014-06-01
ilo.brenz.pl,FQDN,outbound,mtc_malwaredns,Malware,2014-06-01
utenti.lycos.it,FQDN,outbound,mtc_malwaredns,Malware,2014-06-01
bgr.runk.pl,FQDN,outbound,mtc_malwaredns,Malware,2014-06-01
```

### Copyright Info
Originally based on ArcOSI / BadHarvest from Greg Martin

Copyright 2012 GCM Security LLC.

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
