#!/usr/bin/env python
# encoding: utf-8
"""
Universal Acceptance of TLDs

Copyright (c) 2006 ICANN. All rights reserved.

2005-12-04
    v0.4 Kim Davies <kim.davies@icann.org>
2005-10-31
    v0.3 Kim Davies <kim.davies@icann.org>
2005-10-28
    v0.2 Kim Davies <kim.davies@icann.org>
2006-09-24
    v0.1 Kim Davies <kim.davies@icann.org>

TODO:
  * should retry/backoff live lookups a couple of times on failure
  * command line functionality, should be able to be invoked
    like "tldverify update" will update tld list, "tldverify check foo.com"
    will test, etc.

* Copyright (c) 2006, ICANN. All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*
*     * Redistributions of source code must retain the above copyright
*       notice, this list of conditions and the following disclaimer.
*     * Redistributions in binary form must reproduce the above copyright
*       notice, this list of conditions and the following disclaimer in the
*       documentation and/or other materials provided with the distribution.
*     * Neither the name of ICANN nor the names of its contributors may be 
*       used to endorse or promote products derived from this software 
*       without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY ICANN AND CONTRIBUTORS ``AS IS'' AND ANY
* EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL ICANN OR CONTRIBUTORS BE LIABLE FOR ANY
* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

import dns.resolver
import getopt
import os
import string
import sys
import urllib2
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

help_message = __doc__ = """
tldverify.py
"""

class TLDVerifyError(Exception):
    """ All exceptions from this module should derive from this class """
    pass


class DownloadError(Exception):
    pass


class TimeoutError(Exception):
    pass


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def verifytld(domain):

    domain = striptld(domain)

    try:
        answers = dns.resolver.query(domain+".", 'SOA')
    except (dns.resolver.NXDOMAIN):
        return False
    except (dns.resolver.NoAnswer):
        return True
    except (dns.resolver.Timeout):
        raise TimeoutError

    if len(answers)>0:
        return True

    return False


def striptld(domain):

    # strip trailing dot if exists
    #
    if domain[-1:] == ".":
        domain = domain[0:-1]

    return domain[domain.rfind(".")+1:]


def verifytldoffline(domain, dbfile="/tmp/tlds-alpha-by-domain.txt"):

    tldlist = open(dbfile).read()
    validtlds = string.split(tldlist, "\n")
    validtlds = validtlds[1:-1] # first and last lines are cruft

    tld = striptld(domain)

    for v in validtlds:
        if v.upper() == tld.upper():
            return True
    return False


def urlasstring(url):

    data = urllib2.urlopen(url).read()
    return data


def refreshtlddb(dbfile="/tmp/tlds-alpha-by-domain.txt"):

    # Download IANA list of valid TLDs, plus the hash of that file
    #
    try:
        tldlist = urlasstring("http://data.iana.org/TLD/tlds-alpha-by-domain.txt")
        tldmd5 = urlasstring("http://data.iana.org/TLD/tlds-alpha-by-domain.txt.md5")
    except urllib2.URLError, e:
        raise DownloadError("Failed to fetch TLD list or checksum: %s" % e)

    # Verify the file was pulled correctly -- MD5 hash must match
    #
    digest = md5(tldlist).hexdigest()
    if tldmd5[0:32] != digest:
        raise DownloadError("Checksum verification failed: %s != %s" % (tldmd5[0:32], digest))

    # Write obtained file to disk
    #
    fh = open(dbfile+".tmp", "wb")
    fh.write(tldlist)
    fh.close()

    # Reread and verify it was written correctly
    #
    fc = open(dbfile+".tmp", "rb").read()
    digest = md5(fc).hexdigest()
    if tldmd5[0:32] != digest:
        raise DownloadError("Checksum verification failed: %s != %s" % (tldmd5[0:32], digest))

    # Write confirmed -- move to permanent location
    #
    os.rename(dbfile+".tmp", dbfile)


if __name__ == "__main__":

    print "This provides no command line functionality (yet.)"
    sys.exit(2)
