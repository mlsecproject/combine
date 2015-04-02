from yapsy.IPlugin import IPlugin
import re
import bs4
import datetime

class PluginOne(IPlugin):
    NAME = "botscout"
    DIRECTION = "inbound"
    URLS = ['http://botscout.com/last_caught_cache.htm']

    def get_URLs(self):
        return self.URLS

    def get_direction(self):
        return self.DIRECTION

    def get_name(self):
        return self.NAME

    def process_data(self, source, response):
        current_date = str(datetime.date.today())
        data = []
        ip_regex = '^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        soup = bs4.BeautifulSoup(response)
        rows = soup.findAll('tr')
        for row in rows:
            cells = row.findChildren('td')
            count = 0
            ip = ''
            note = ''
            for cell in cells:
                if count == 0:
                    note = "bot_name:" + cell.string + "|||"
                if count == 1:
                    note += "bot_email:" + cell.string
                if count == 2:
                    ip = cell.string
                count += 1
            if re.match(ip_regex, ip):
                data.append({'indicator':ip, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'C2/Bot', 'date':current_date})
        return data
