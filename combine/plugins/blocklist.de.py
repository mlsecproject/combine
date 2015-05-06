import datetime

from yapsy.IPlugin import IPlugin


class PluginOne(IPlugin):
    NAME = "blocklist.de"
    DIRECTION = "inbound"
    URLS = ['http://www.blocklist.de/lists/ssh.txt',
            'http://www.blocklist.de/lists/apache.txt',
            'http://www.blocklist.de/lists/asterisk.txt',
            'http://www.blocklist.de/lists/bots.txt',
            'http://www.blocklist.de/lists/courierimap.txt',
            'http://www.blocklist.de/lists/courierpop3.txt',
            'http://www.blocklist.de/lists/email.txt',
            'http://www.blocklist.de/lists/ftp.txt',
            'http://www.blocklist.de/lists/imap.txt',
            'http://www.blocklist.de/lists/ircbot.txt',
            'http://www.blocklist.de/lists/pop3.txt',
            'http://www.blocklist.de/lists/postfix.txt',
            'http://www.blocklist.de/lists/proftpd.txt',
            'http://www.blocklist.de/lists/sip.txt']

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
                data.append({'indicator': i, 'indicator_type': "IPv4", 'indicator_direction': self.DIRECTION,
                             'source_name': self.NAME, 'source': source, 'date': current_date})
        return data
