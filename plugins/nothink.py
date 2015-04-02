from yapsy.IPlugin import IPlugin
import datetime
import uniaccept
import os
import re

class PluginOne(IPlugin):
    NAME = "nothink"
    DIRECTION = "outbound"
    URLS = ['http://www.nothink.org/blacklist/blacklist_malware_dns.txt',
            'http://www.nothink.org/blacklist/blacklist_malware_http.txt',
            'http://www.nothink.org/blacklist/blacklist_malware_irc.txt',
            'http://www.nothink.org/blacklist/blacklist_ssh_day.txt']

    def get_URLs(self):
        return self.URLS

    def get_direction(self):
        return self.DIRECTION

    def get_name(self):
        return self.NAME

    def indicator_type(self, indicator):
        ip_regex = '^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$' 
        if re.match(ip_regex, indicator):
            return "IPv4"
        if uniaccept.verifytldoffline(indicator, "./tld-list.txt"):
            return "FQDN"
        else:
            return None

    def process_data(self, source, response):
        if not os.path.isfile('./tld-list.txt'):
            uniaccept.refreshtlddb("./tld-list.txt")
        data = []
        current_date = str(datetime.date.today())
        for line in response.splitlines():
            if not line.startswith('#') and not line.startswith('/') and not line.startswith('Export date') and len(line) > 0:
                i = line.split()[0]
                if 'ssh_day' in source:
                    data.append({'indicator':i, 'indicator_type':self.indicator_type(i), 'indicator_direction':'inbound',
                             'source_name':self.NAME, 'source':source, 'note':'Malware', 'date':current_date})
                else:
                    data.append({'indicator':i, 'indicator_type':self.indicator_type(i), 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'SSH Bruteforce', 'date':current_date})
        return data
