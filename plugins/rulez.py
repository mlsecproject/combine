from yapsy.IPlugin import IPlugin

class PluginOne(IPlugin):
    NAME = "rulez"
    DIRECTION = "inbound"
    URLS = ['http://danger.rulez.sk/projects/bruteforceblocker/blist.php']

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
                i = line.partition('#')[0].strip()
                date = line.partition('#')[2].split(' ')[1]
                data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'Bruteforce IP', 'date':date})
        return data
