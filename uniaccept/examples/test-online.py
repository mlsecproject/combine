#!/usr/bin/env python
#

import uniaccept
import sys

try:
    domain = sys.argv[1]
except:
    print "Usage: %s [domain]" % (sys.argv[0])
    sys.exit(2)

result = uniaccept.verifytld(domain)

if result == True:
    print "%s contains a valid TLD" % (domain)
    sys.exit(0)
else:
    print "%s does NOT contain a valid TLD" % (domain)
    sys.exit(1)

