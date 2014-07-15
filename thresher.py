import datetime
import json
import re


def indicator_type(indicator):
    ip_regex = '\b(?P<address>(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))\b'
    if re.match(ip_regex, indicator):
        return "IPv4"
    else:
        return None


def process_simple_list(response, source, direction):
    return [(i, indicator_type(i), direction, source, '', '%s' % datetime.date.today()) for i in response.split('\n')]


def thresh(file_name):
    with open(file_name, 'rb') as f:
        crop = json.load(f)

    harvest = []
    thresher_map = {'blocklist': process_simple_list}

    for response in crop:
        if response[1] == 200:
            if 'blocklist.de' in response[0]:
                harvest += thresher_map['blocklist'](response[2], response[0], 'inbound')
            else:
                pass
        else:
            pass


if __name__ == "__main__":
    thresh('harvest.json')