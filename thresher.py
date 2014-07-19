import bs4
import datetime
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
    for line in response.split('\n'):
        if not line.startswith('#') and len(line) > 0:
            i = line.split()[0]
            data.append((i, indicator_type(i), direction, source, '', '%s' % datetime.date.today()))
    return data


def process_project_honeypot(response, source, direction):
    soup = bs4.BeautifulSoup(response)
    return [(i.text, indicator_type(i.text), direction, source, '', '%s' % datetime.date.today()) for i in soup.find_all('a', 'bnone')]


def process_drg(response, source, direction):
    data = []
    for line in response.split('\n'):
        if not line.startswith('#') and len(line) > 0:
            i = line.split('|')[2].strip()
            data.append((i, indicator_type(i), direction, source, '', '%s' % datetime.date.today()))
    return data


def process_alienvault(response, source, direction):
    data = []
    for line in response.split('\n'):
        if not line.startswith('#') and len(line) > 0:
            i = line.partition('#')[0].strip()
            data.append((i, indicator_type(i), direction, source, '', '%s' % datetime.date.today()))
    return data


def process_packetmail(response, source, direction):
    data = []
    for line in response.split('\n'):
        if not line.startswith('#') and len(line) > 0:
            i = line.partition(';')[0].strip()
            data.append((i, indicator_type(i), direction, source, '', '%s' % datetime.date.today()))
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
                    'rulez': process_alienvault,
                    'sans': process_simple_list,
                    'nothink': process_simple_list,
                    'packetmail': process_packetmail,
                    'dragonresearchgroup': process_drg}

    for response in crop:
        if response[1] == 200:
            for site in thresher_map:
                if site in response[0]:
                    harvest += thresher_map[site](response[2], response[0], 'inbound')
                else:  # how to handle non-mapped sites?
                    pass
        else:  # how to handle non-200 non-404?
            pass

    with open(output_file, 'wb') as f:
        json.dump(harvest, f, indent=2)


if __name__ == "__main__":
    thresh('harvest.json', 'crop.json')
