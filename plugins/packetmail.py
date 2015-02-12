from yapsy.IPlugin import IPlugin
import datetime

class PluginOne(IPlugin):
    NAME = "packetmail"
    DIRECTION = "inbound"
    URLS = ['https://www.packetmail.net/iprep.txt']

    def get_URLs(self):
        return self.URLS

    def get_direction(self):
        return self.DIRECTION

    def get_name(self):
        return self.NAME

    def process_data(self, source, response):
        data = []
        filter_comments = lambda x: not x[0].startswith('#')
        try:
            for line in ifilter(filter_comments,
                                reader(response.splitlines(), delimiter=';')):
                i = line[0]
                date = line[1].split(' ')[1]
                data.append((i, "IPv4", self.DIRECTION, self.NAME, '', date))
        except (IndexError, AttributeError):
            pass
        return data
