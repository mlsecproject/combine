from yapsy.IPlugin import IPlugin
import uniaccept
import re
import bs4
import datetime

class PluginOne(IPlugin):
    NAME = "clean-mx"
    DIRECTION = "hash"
    URLS = ['http://support.clean-mx.de/clean-mx/xmlviruses.php?']

    def get_URLs(self):
        return self.URLS

    def get_direction(self):
        return self.DIRECTION

    def get_name(self):
        return self.NAME

    def process_data(self, source, response):
        uniaccept.refreshtlddb("./tld-list.txt")
        current_date = str(datetime.date.today())
        data = []
        ip_regex = '^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        soup = bs4.BeautifulSoup(response)
        entries = soup.findAll('entry')
        for entry in entries:
            md5 = entry.findAll('md5')[0].text
            virusname = entry.findAll('virusname')[0].text
            url = entry.findAll('url')[0].text
            ip = entry.findAll('ip')[0].text
            asn = entry.findAll('as')[0].text
            domain = entry.findAll('domain')[0].text
            note = "%s|||%s|||%s|||%s|||%s" %(virusname, url, ip, asn, domain)
            note = ''.join([x.replace('\x00','').encode("utf8") for x in note.split()])
            if md5 != None and md5 != '':
                data.append((md5, "md5", self.DIRECTION, self.NAME, note, current_date))
            if re.match(ip_regex, ip):
                data.append((ip, "IPv4", 'outbound', self.NAME, asn, current_date))
            if uniaccept.verifytldoffline(domain, "./tld-list.txt") == True:
                data.append((domain, "FQDN", 'outbound', self.NAME, url, current_date))
        return data
