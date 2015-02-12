from yapsy.IPlugin import IPlugin
import datetime
import uniaccept
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
        result = uniaccept.verifytldoffline(indicator, "./tld-list.txt")
        if result == True:
            return "FQDN"
        else:
            # TODO add hash support
            return None

    def process_data(self, source, response):
        # Update TLD db
        uniaccept.refreshtlddb("./tld-list.txt")
        data = []
        current_date = str(datetime.date.today())
        for line in response.splitlines():
            if not line.startswith('#') and not line.startswith('/') and not line.startswith('Export date') and len(line) > 0:
                i = line.split()[0]
                if 'ssh_day' in source:
                    data.append((i, self.indicator_type(i), 'inbound', self.NAME, '', current_date))
                else:
                    data.append((i, self.indicator_type(i), self.DIRECTION, self.NAME, '', current_date))
        return data
