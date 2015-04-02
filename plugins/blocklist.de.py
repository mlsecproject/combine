from yapsy.IPlugin import IPlugin
import datetime

class PluginOne(IPlugin):
    NAME = "blocklist.de"
    DIRECTION = "inbound"
    URLS = ['http://lists.blocklist.de/lists/ssh.txt',
			'http://lists.blocklist.de/lists/mail.txt',
			'http://lists.blocklist.de/lists/apache.txt',
			'http://lists.blocklist.de/lists/imap.txt',
			'http://lists.blocklist.de/lists/ftp.txt',
			'http://lists.blocklist.de/lists/bots.txt',
			'http://lists.blocklist.de/lists/strongips.txt',
			'http://lists.blocklist.de/lists/bruteforcelogin.txt']

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
                if 'ssh' in source:
                    data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'SSH Attack', 'date':current_date})
                if 'mail' in source:
                    data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'Mailserver attack', 'date':current_date})
		if 'apache' in source:
                    data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'Apache/RFI Attack', 'date':current_date})
                if 'imap' in source:
                    data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'IMAP Attack', 'date':current_date})
                if 'ftp' in source:
                    data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'FTP Attack', 'date':current_date})
		if 'bots' in source:
                    data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'IP Bot', 'date':current_date})
                if 'strongips' in source:
                    data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'Malicious IP', 'date':current_date})
                if 'bruteforcelogin' in source:
                    data.append({'indicator':i, 'indicator_type':"IPv4", 'indicator_direction':self.DIRECTION,
                             'source_name':self.NAME, 'source':source, 'note':'Bruteforce Attack', 'date':current_date})
        return data
