#!/usr/bin/env python
# Harvest
# Scrapes OSINT data and converts to csv
#----------------------------------------------------------------------------
#
# Originally based on ArcOSI / BadHarvest from Greg Martin
# Copyright 2012 GCM Security LLC.
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#----------------------------------------------------------------------------
#
# Copyright 2014 MLSec Project
#
# Licensed under GPLv3 - https://github.com/mlsecproject/combine/blob/master/LICENSE
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
import csv
import urllib2, re, socket, time, os, argparse, sys
import ConfigParser


def find_content(url, regex, comment_ignore_set):
    try:
        req = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36' })
        content = urllib2.urlopen(req).read()
        print 'Grabbing list from: ' + url
        time.sleep(1)
        for ix in xrange(len(COMMENT_REGEXES)):
            if not COMMENT_REGEXES_NAMES[ix] in comment_ignore_set:
                content = re.sub(COMMENT_REGEXES[ix],
                                 "\n" if COMMENT_REGEXES[ix].pattern.find("\\n") >= 0 else "", content)
        return re.finditer(regex, content)
    except:
        print 'Failed connection to: ' + url + ' skipping...'
        return None


def syslog(message):
    pass


def build_intel():
    ## Opening local file to dump output
    csv_writer = None
    file_handler = None
    if localfile:
        print 'Outputing csv to "' + localfile + '"'
        file_handler = open(localfile, 'w')
        csv_writer = csv.writer(file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(["domain", "ip", "category", "source"])

    for addr_type in ["domain", "ip"]:
        addr_type_upper = addr_type.upper()
        sources_cgf = addr_type_upper + "SOURCES"
        sources_regex_cgf = sources_cgf + "REGEX"
        sources_comment_ignore = sources_cgf + "COMMENTIGNORE"
        sources_cat_cgf = sources_cgf + "CATEGORIES"
        sources_whitelist = CONFIG[addr_type_upper + "WHITELIST"]
        sources_count = 0
        for src_nam, src_url in CONFIG[sources_cgf].items():
            sources_count += 1
            val_regex = CONFIG["DEFAULTS"][addr_type + "_regex"]
            comment_ignore_set = set()
            if src_nam in CONFIG[sources_regex_cgf]:
                val_regex = CONFIG[sources_regex_cgf][src_nam]
            if src_nam in CONFIG[sources_comment_ignore]:
                val_comment_ignore = CONFIG[sources_comment_ignore][src_nam].split(',')
                for x in val_comment_ignore:
                    comment_ignore_set.add(x.strip())
            categories = [CONFIG["DEFAULTS"]["category"]]
            if src_nam in CONFIG[sources_cat_cgf]:
                categories = [x.strip() for x in CONFIG[sources_cat_cgf][src_nam].split(",")]
            matches = find_content(src_url, val_regex, comment_ignore_set)
            added_set = set()
            if matches is not None:
                for reg_match in matches:
                    addr = reg_match.group("address")
                    if addr in sources_whitelist or addr in added_set:
                            continue
                    if localfile:
                        for category in categories:
                            csv_writer.writerow([addr if addr_type == "domain" else "",
                                                 addr if addr_type == "ip" else "",
                                                 category,
                                                 src_nam])
                    added_set.add(addr)
        print '%s sources: %d' % (addr_type, sources_count)
    if localfile:
        file_handler.close()

if __name__ == "__main__":

    SECTIONS = ['PROXY', 'DEFAULTS',
                'IPSOURCES', 'IPSOURCESREGEX', 'IPSOURCESCOMMENTIGNORE', 'IPSOURCESCATEGORIES', 'IPWHITELIST',
                'DOMAINSOURCES', 'DOMAINSOURCESREGEX', 'DOMAINSOURCESCOMMENTIGNORE',
                'DOMAINSOURCESCATEGORIES', 'DOMAINWHITELIST']  # Keep ordering

    parser = argparse.ArgumentParser(description="Download blacklists from badharvest",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-config",
                        type=str,
                        default="harvest.cfg",
                        help="""a configuration file with the following syntax could be provided:

    [PROXY]
    enabled = no
    host = proxy.localhost
    port = 3128
    user = none
    pass = none

    [DEFAULTS]
    category = outbound
    ip_regex = a regex with a group named address to be captured
    domain_regex = a regex with a group named address to be captured
    comment_regex_1 = first regex to identify comments
    comment_regex_2 = second regex to identify comments
    ...
    comment_regex_n = nth regex to identify comments

    [IPSOURCES]
    name_1 = url with ip sources (any name is valid)

    [IPSOURCESREGEX]
    name_1 = regex of ipsource named name_1 (if not specified will default to ip_regex)

    [IPSOURCESCOMMENTIGNORE]
    name_1 = comma separated values of comment regex names to be ignored for ipsource name_1

    [IPSOURCESCATEGORIES]
    name_1 = comma separated values of categories to be associated with ipsource name_1

    [IPWHITELIST]
    ip1 = whitelisted ip 1
    ip2 = whitelisted ip 2
    ...
    ipn = whitelisted ip n

    [DOMAINSOURCES]
    name_1 = url with domain sources. any name is valid

    [DOMAINSOURCESREGEX]
    name_1 = regex of domainsource named name_1 (if not specified will default to domain_regex)

    [DOMAINSOURCESCOMMENTIGNORE]
    name_1 = comma separated values of comment regex names to be ignored for domainsource name_1

    [DOMAINSOURCESCATEGORIES]
    name_1 = comma separated values of categories to be associated with domainsource name_1

    [DOMAINWHITELIST]
    d1 = whitelisted domain 1
    d2 = whitelisted domain 2
    ...
    dn = whitelisted domain n
                            """)
    parser.add_argument("-output",
                        default="harvest.csv",
                        #required=True,
                        help="csv output file")

    args = vars(parser.parse_args())
    localfile = args['output']
    config_file = args['config']

    #Default configuration
    CONFIG = {}

    #Sections which can be override by config file

    #Override default configuration with config file content if provided
    config_parser = ConfigParser.ConfigParser()
    if config_file != "":
        if os.access(config_file, os.R_OK):
            config_parser.read(config_file)

            for section in config_parser.sections():
                if section not in SECTIONS:
                    continue

                is_regex_section = section.endswith("REGEX")
                is_deafult_section = section == "DEFAULTS"
                CONFIG[section] = {}
                for option, value in config_parser.items(section):
                    CONFIG[section][option] = value
                    if "regex" in option or is_regex_section:
                        CONFIG[section][option] = re.compile(CONFIG[section][option], re.IGNORECASE)
                    if is_deafult_section and "comment_regex" in option:
                        if "comment_regex" not in CONFIG[section]:
                            CONFIG[section]["comment_regex"] = []
                            CONFIG[section]["comment_regex_name"] = []
                        elif not isinstance(CONFIG[section]["comment_regex"], list):
                            CONFIG[section]["comment_regex"] = [CONFIG[section]["comment_regex"]]
                            CONFIG[section]["comment_regex_name"] = [CONFIG[section]["comment_regex_name"]]
                        if option != "comment_regex":
                            CONFIG[section]["comment_regex"].append(CONFIG[section][option])
                            CONFIG[section]["comment_regex_name"].append(option)
                if section.endswith("WHITELIST"):
                    CONFIG[section] = set(CONFIG[section].values())

        else:
            print "Unable to load configuration file: %s" % config_file
            sys.exit(-1)

    # Set Global Timeout
    socket.setdefaulttimeout(30)
    COMMENT_REGEXES = CONFIG["DEFAULTS"]["comment_regex"]
    COMMENT_REGEXES_NAMES = CONFIG["DEFAULTS"]["comment_regex_name"]
    #Main

    #Check/Initialize  Config
    if 'enabled' in CONFIG and CONFIG['PROXY']['enabled'] in ['y', 'yes']:
        proxy_support = urllib2.ProxyHandler({
            "http": "http://%(user)s:%(pass)s@%(host)s:%(port)s" % CONFIG['PROXY'],
            "https": "http://%(user)s:%(pass)s@%(host)s:%(port)s" % CONFIG['PROXY']})
        opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)

    # Go scraper
    build_intel()
