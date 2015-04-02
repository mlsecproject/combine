from yapsy.IPlugin import IPlugin
import feedparser
import datetime

class PluginOne(IPlugin):
    NAME = "projecthoneypot"
    DIRECTION = "inbound"
    URLS = ['http://www.projecthoneypot.org/list_of_ips.php?rss=1']

    def get_URLs(self):
        return self.URLS

    def get_direction(self):
        return self.DIRECTION

    def get_name(self):
        return self.NAME

    def process_data(self, source, response):
        data = []
        for entry in feedparser.parse(response).entries:
            i = entry.title.partition(' ')[0]
            i_date = entry.description.split(' ')[-1]
            data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'Malicious IP', 'date':i_date})
        return data
