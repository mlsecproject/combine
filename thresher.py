import bs4
import datetime
import feedparser
import json
import re


def indicator_type(indicator):
    ip_regex = '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
    domain_regex = '(www\.)?(?P<address>([\d\w.][-\d\w.]{0,253}[\d\w.]+\.)+(AC|AD|AE|AERO|AF|AG|AI|AL|AM|AN|AO|AQ|AR|ARPA|AS|ASIA|AT|AU|AW|AX|AZ|BA|BB|BD|BE|BF|BG|BH|BI|BIZ|BJ|BM|BN|BO|BR|BS|BT|BV|BW|BY|BZ|CA|CAT|CC|CD|CF|CG|CH|CI|CK|CL|CM|CN|COM|COOP|CR|CU|CV|CX|CY|CZ|DE|DJ|DK|DM|DO|DZ|EC|EDU|EE|EG|ER|ES|ET|EU|FI|FJ|FK|FM|FO|FR|GA|GB|GD|GE|GF|GG|GH|GI|GL|GM|GN|GOV|GP|GQ|GR|GS|GT|GU|GW|GY|HK|HM|HN|HR|HT|HU|ID|IE|IL|IM|INFO|INT|IO|IQ|IR|IS|IT|JE|JM|JO|JOBS|JP|KE|KG|KH|KI|KM|KN|KP|KR|KW|KY|KZ|LA|LB|LC|LI|LK|LR|LS|LT|LU|LV|LY|MA|MC|MD|ME|MG|MH|MIL|MK|ML|MM|MN|MO|MOBI|MP|MQ|MR|MS|MT|MU|MUSEUM|MV|MW|MX|MY|MZ|NA|NAME|NC|NET|NF|NG|NI|NL|NO|NP|NR|NU|NZ|OM|ORG|PA|PE|PF|PG|PH|PK|PL|PM|PN|PR|PRO|PS|PT|PW|PY|QA|RE|RO|RS|RU|RW|SA|SB|SC|SD|SE|SG|SH|SI|SJ|SK|SL|SM|SN|SO|SR|ST|SU|SV|SY|SZ|TC|TD|TEL|TF|TG|TH|TJ|TK|TL|TM|TN|TO|TP|TR|TRAVEL|TT|TV|TW|TZ|UA|UG|UK|US|UY|UZ|VA|VC|VE|VG|VI|VN|VU|WF|WS|XN|XN|XN|XN|XN|XN|XN|XN|XN|XN|XN|YE|YT|YU|ZA|ZM|ZW))'

    if re.match(ip_regex, indicator):
        return "IPv4"
    elif re.match(domain_regex, indicator):
        return "DNS"
    else:
        return None


def process_simple_list(response, source, direction):
    data = []
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            i = line.split()[0]
            data.append((i, indicator_type(i), direction, source, '', '%s' % datetime.date.today()))
    return data


def process_sans(response, source, direction):
    data = []
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            i = line.split()[0]
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
    for entry in feedparse.parse(response):
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
            data.append((i, indicator_type(i), direction, source, note, date))
    return data


def thresh(input_file, output_file):
    with open(input_file, 'rb') as f:
        crop = json.load(f)

    harvest = []
    thresher_map = {'blocklist.de': process_simple_list,
                    'openbl': process_simple_list,
                    'projecthoneypot': process_project_honeypot,
                    'ciarmy': process_simple_list,
                    'alienvault': process_alienvault,
                    'rulez': process_rulez,
                    'sans': process_sans,
                    'nothink': process_simple_list,
                    'packetmail': process_packetmail,
                    'autoshun': process_autoshun,
                    'the-haleys': process_haleys,
                    'virbl': process_simple_list,
                    'dragonresearchgroup': process_drg,
                    'malwaregroup': process_malwaregroup}

    for response in crop['inbound']:
        if response[1] == 200:
            for site in thresher_map:
                if site in response[0]:
                    harvest += thresher_map[site](response[2], response[0], 'inbound')
                else:  # how to handle non-mapped sites?
                    pass
        else:  # how to handle non-200 non-404?
            pass

    for response in crop['outbound']:
        if response[1] == 200:
            for site in thresher_map:
                if site in response[0]:
                    harvest += thresher_map[site](response[2], response[0], 'outbound')
                else:  # how to handle non-mapped sites?
                    pass
        else:  # how to handle non-200 non-404?
            pass
    with open(output_file, 'wb') as f:
        json.dump(harvest, f, indent=2)


if __name__ == "__main__":
    thresh('harvest.json', 'crop.json')
