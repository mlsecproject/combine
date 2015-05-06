#!/usr/bin/env python
#

import uniaccept
import sys

try:
    domain = sys.argv[1]
except:
    print "Usage: %s [domain]" % (sys.argv[0])
    sys.exit(2)

#
#  NOTE! This is for demonstration purposes. You should not fetch this
#  file every time you want to do a test -- instead it should be cached
#  locally and not redownloaded more often than once every 24 hours.
#
uniaccept.refreshtlddb("/tmp/tld-list.txt")

#
#  Perform query
#
result = uniaccept.verifytldoffline(domain, "/tmp/tld-list.txt")

if result == True:
    print "%s contains a valid TLD" % (domain)
    sys.exit(0)
else:
    print "%s does NOT contain a valid TLD" % (domain)
    sys.exit(1)

