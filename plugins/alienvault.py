from yapsy.IPlugin import IPlugin
import datetime

class PluginOne(IPlugin):
    NAME = "alienvault"
    DIRECTION = "outbound"
    URLS = ['http://reputation.alienvault.com/reputation.data']

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
            if not line.startswith('#') and len(line) > 0:
                i = line.partition('#')[0].strip()
                note = line.split('#')[3].strip()
                if 'Scanning Host' in note or 'Spamming' in note:
                    data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':'inbound', 
                                 'source_name':self.NAME, 'source':source, 'note':'Scanning Host/Spamming', 'date':current_date})
                elif 'Malware' in note or 'C&C' in note or 'APT' in note:
                    data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':'outbound', 
                                 'source_name':self.NAME, 'source':source, 'note':'Malware/C2C', 'date':current_date})
        return data
