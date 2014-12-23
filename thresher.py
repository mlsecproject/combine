import ConfigParser
import bs4
import datetime
import feedparser
import json
import re
import sys
from logger import get_logger
import logging

logger = get_logger('thresher')

def indicator_type(indicator):
    ip_regex = '^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    domain_regex = '(www\.)?(?P<address>([\d\w.][-\d\w.]{0,253}[\d\w.]+\.)+(AC|AD|AE|AERO|AF|AG|AI|AL|AM|AN|AO|AQ|AR|ARPA|AS|ASIA|AT|AU|AW|AX|AZ|BA|BB|BD|BE|BF|BG|BH|BI|BIZ|BJ|BM|BN|BO|BR|BS|BT|BV|BW|BY|BZ|CA|CAT|CC|CD|CF|CG|CH|CI|CK|CL|CM|CN|COM|COOP|CR|CU|CV|CX|CY|CZ|DE|DJ|DK|DM|DO|DZ|EC|EDU|EE|EG|ER|ES|ET|EU|FI|FJ|FK|FM|FO|FR|GA|GB|GD|GE|GF|GG|GH|GI|GL|GM|GN|GOV|GP|GQ|GR|GS|GT|GU|GW|GY|HK|HM|HN|HR|HT|HU|ID|IE|IL|IM|IN|INFO|INT|IO|IQ|IR|IS|IT|JE|JM|JO|JOBS|JP|KE|KG|KH|KI|KM|KN|KP|KR|KW|KY|KZ|LA|LB|LC|LI|LK|LR|LS|LT|LU|LV|LY|MA|MC|MD|ME|MG|MH|MIL|MK|ML|MM|MN|MO|MOBI|MP|MQ|MR|MS|MT|MU|MUSEUM|MV|MW|MX|MY|MZ|NA|NAME|NC|NET|NF|NG|NI|NL|NO|NP|NR|NU|NZ|OM|ORG|PA|PE|PF|PG|PH|PK|PL|PM|PN|PR|PRO|PS|PT|PW|PY|QA|RE|RO|RS|RU|RW|SA|SB|SC|SD|SE|SG|SH|SI|SJ|SK|SL|SM|SN|SO|SR|ST|SU|SV|SY|SZ|TC|TD|TEL|TF|TG|TH|TJ|TK|TL|TM|TN|TO|TP|TR|TRAVEL|TT|TV|TW|TZ|UA|UG|UK|US|UY|UZ|VA|VC|VE|VG|VI|VN|VU|WF|WS|XN|XN|XN|XN|XN|XN|XN|XN|XN|XN|XN|YE|YT|YU|ZA|ZM|ZW))'

    if re.match(ip_regex, indicator):
        return "IPv4"
    # TODO: Update domain name validation (cf. #15)
    elif re.match(domain_regex, indicator, re.IGNORECASE):
        return "FQDN"
    else:
        return None


def process_simple_list(response, source, direction):
    data = []
    for line in response.splitlines():
        if not line.startswith('#') and not line.startswith('/') and not line.startswith('Export date') and len(line) > 0:
            i = line.split()[0]
            data.append((i, indicator_type(i), direction, source, '', '%s' % datetime.date.today()))
    return data


def process_sans(response, source, direction):
    data = []
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            # Because SANS zero-pads their addresses
            i = re.sub('\.0{1,2}', '.', line.split()[0].lstrip('0'))
            date = line.split()[-1]
            data.append((i, indicator_type(i), direction, source, '', date))
    return data


def process_virbl(response, source, direction):
    data = []
    for line in response.splitlines():
        if not line.startswith('E') and len(line) > 0:
            i = line.split()[0]
            data.append((i, indicator_type(i), direction, source, '', '%s' % datetime.date.today()))
    return data


def process_project_honeypot(response, source, direction):
    data = []
    for entry in feedparser.parse(response).entries:
        i = entry.title.partition(' ')[0]
        i_date = entry.description.split(' ')[-1]
        data.append((i, indicator_type(i), direction, source, '', i_date))
    return data


def process_drg(response, source, direction):
    data = []
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            i = line.split('|')[2].strip()
            data.append((i, indicator_type(i), direction, source, '', '%s' % datetime.date.today()))
    return data


def process_alienvault(response, source, direction):
    data = []
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            i = line.partition('#')[0].strip()
            note = line.split('#')[3].strip()
            if 'Scanning Host' in note or 'Spamming' in note:
                direction = 'inbound'
            elif 'Malware' in note or 'C&C' in note or 'APT' in note:
                direction = 'outbound'
            data.append((i, indicator_type(i), direction, source, note, '%s' % datetime.date.today()))
    return data


def process_rulez(response, source, direction):
    data = []
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            i = line.partition('#')[0].strip()
            date = line.partition('#')[2].split(' ')[1]
            data.append((i, indicator_type(i), direction, source, '', date))
    return data


def process_packetmail(response, source, direction):
    data = []
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            i = line.partition(';')[0].strip()
            date = line.split('; ')[1].split(' ')[0]
            data.append((i, indicator_type(i), direction, source, '', date))
    return data


def process_autoshun(response, source, direction):
    data = []
    if response.startswith("Couldn't select database"):
        return data
    for line in response.splitlines():
        if not line.startswith('S') and len(line) > 0:
            i = line.partition(',')[0].strip()
            date = line.split(',')[1].split()[0]
            note = line.split(',')[-1]
            data.append((i, indicator_type(i), direction, source, note, date))
    return data


def process_haleys(response, source, direction):
    data = []
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            i = line.partition(':')[2].strip()
            data.append((i, indicator_type(i), direction, source, '', '%s' % datetime.date.today()))
    return data


def process_malwaregroup(response, source, direction):
    data = []
    soup = bs4.BeautifulSoup(response)
    for row in soup.find_all('tr'):
        if row.td:
            i = row.td.text
            date = row.contents[-1].text
            data.append((i, indicator_type(i), direction, source, '', date))
    return data

def parse_feed_response(feed_response, category, parsers_list):
    """ Expect in input:
        - feed_response: list(respnsecontent, status, label)
        - category: str
        - parsers_list: dict

        return the parsed response
        raise an exception if the response status is not 200
    """
    if feed_response[1] == 200:
        for count, (plabel, parser) in enumerate(parsers_list.iteritems()):
            if plabel == feed_response[0]:
                logger.info('Parsing feed from %s with parser "%s"' % (feed_response[0], parser))
                return globals()[parser](feed_response[2], feed_response[0], category)
            
            # If even the last element do not match, use the standard parser
            if count == len(parsers_list) - 1: 
                logger.info('Parsing feed from %s with parser "process_simple_list"' % feed_response[0])
                return process_simple_list(feed_response[2], feed_response[0], category)
    else:
        raise Exception('Could not handle %s: %s' % (feed_response[0], feed_response[1]))

def thresh(input_file, output_file):
    config = ConfigParser.SafeConfigParser(allow_no_value=False)
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        logger.error('Thresher: Could not read combine.cfg.')
        logger.error('HINT: edit combine-example.cfg and save as combine.cfg.')
        return

    parsers_list = dict(config.items('feeds.parsers'))

    logger.info('Loading raw feed data from %s' % input_file)
    with open(input_file, 'rb') as f:
        crop = json.load(f)

    harvest = []

    for response in crop['inbound']:
        logger.info('Evaluating %s' % response[0])
        try:
            harvest += parse_feed_response(response, 'inbound', parsers_list)
        except Exception, e:
            logger.error(e)

    for response in crop['outbound']:
        logger.info('Evaluating %s' % response[0])
        try:
            harvest += parse_feed_response(response, 'outbound', parsers_list)
        except Exception, e:
            logger.error(e)

    logger.info('Storing parsed data in %s' % output_file)
    with open(output_file, 'wb') as f:
        json.dump(harvest, f, indent=2)


if __name__ == "__main__":
    thresh('harvest.json', 'crop.json')
