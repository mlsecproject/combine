from yapsy.IPlugin import IPlugin

class PluginOne(IPlugin):
    NAME = "autoshun"
    DIRECTION = "inbound"
    URLS = ['http://www.autoshun.org/files/shunlist.csv']

    def get_URLs(self):
        return self.URLS

    def get_direction(self):
        return self.DIRECTION

    def get_name(self):
        return self.NAME

    def process_data(self, source, response):
        data = []
        if response.startswith("Couldn't select database"):
            return data
        for line in response.splitlines():
            if not line.startswith('S') and len(line) > 0:
                i = line.partition(',')[0].strip()
                date = line.split(',')[1].split()[0]
                note = line.split(',')[-1]
                data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'Malicious IP', 'date':date})
        return data
