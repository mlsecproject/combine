from yapsy.IPlugin import IPlugin
import re

class PluginOne(IPlugin):
    NAME = "sans"
    DIRECTION = "inbound"
    URLS = ['https://isc.sans.edu/ipsascii.html']

    def get_URLs(self):
        return self.URLS

    def get_direction(self):
        return self.DIRECTION

    def get_name(self):
        return self.NAME

    def process_data(self, source, response):
        data = []
        for line in response.splitlines():
            if not line.startswith('#') and len(line) > 0:
                # Because SANS zero-pads their addresses
                i = re.sub('\.0{1,2}', '.', line.split()[0].lstrip('0'))
                date = line.split()[-1]
                data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'Malicious IP', 'date':date})
        return data
