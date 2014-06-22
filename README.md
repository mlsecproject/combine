combine
=======

Combine gathers OSINT Threat Intelligence Feeds

You can run the original harvest.py tool with a cmd line like this:

````
./harvest.py -config harvest-outbound.cfg -output sample-output.txt
`````

The output will actually be a CSV with the following schema:
```
address, direction, source, date
```

The `address` field consists of a FQDN or IPv4 address. The `direction` field will be either `inbound` or `outbound`. The `date` field will be in `YYYY-MM-DD` format.

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
