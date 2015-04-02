from yapsy.IPlugin import IPlugin
import datetime

class PluginOne(IPlugin):
    NAME = "palevotracker"
    DIRECTION = "outbound"
    URLS = ['https://palevotracker.abuse.ch/blocklist.php?download=ipblocklist',
            'https://palevotracker.abuse.ch/blocklist.php?download=domainblocklist']

    def get_URLs(self):
        return self.URLS

    def get_direction(self):
        return self.DIRECTION

    def get_name(self):
        return self.NAME

    def process_data(self, source, response):
        data = []
        current_date = str(datetime.date.today())
        for line in response.splitlines():
            if not line.startswith('#') and not line.startswith('/') and not line.startswith('Export date') and len(line) > 0:
                i = line.split()[0]
                if 'ipblocklist' in source:
                    data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'Worm Palevo IP', 'date':current_date})
                elif 'domainblocklist' in source:
                    data.append({'indicator':i, 'indicator_type':"FQDN", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'Worm Palevo Domain', 'date':current_date})
        return data
