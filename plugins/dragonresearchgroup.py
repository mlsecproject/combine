from yapsy.IPlugin import IPlugin
import datetime

class PluginOne(IPlugin):
    NAME = "dragonresearchgroup"
    DIRECTION = "inbound"
    URLS = ['http://dragonresearchgroup.org/insight/sshpwauth.txt',
            'http://dragonresearchgroup.org/insight/vncprobe.txt']

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
                i = line.split('|')[2].strip()
                if 'sshpwauth' in source:
                    data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'SSHpwauth', 'date':current_date})
                if 'vncprobe' in source:
                    data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'VNC Probe', 'date':current_date})
        return data
