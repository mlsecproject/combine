import ConfigParser
import bs4
import datetime
import feedparser
import json
import re
import sys
#from logger import get_logger
import logging
from csv import reader
from itertools import ifilter
from yapsy.PluginManager import PluginManager
from logbook.compat import redirect_logging
from logging import getLogger
import uniaccept

redirect_logging()

logging.getLogger('yapsy').setLevel(logging.DEBUG)
logger = getLogger('thresher')

def indicator_type(indicator):
    ip_regex = '^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

    if re.match(ip_regex, indicator):
        return "IPv4"
    result = uniaccept.verifytldoffline(indicator, "./tld-list.txt")
    if result == True:
        return "FQDN"
    else:
        # TODO add hash support
        return None


def process_simple_list(response, source, direction):
    data = []
    current_date = str(datetime.date.today())
    for line in response.splitlines():
        if not line.startswith('#') and not line.startswith('/') and not line.startswith('Export date') and len(line) > 0:
            i = line.split()[0]
            data.append((i, indicator_type(i), direction, source, '', current_date))
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
    current_date = str(datetime.date.today())
    for line in response.splitlines():
        if not line.startswith('E') and len(line) > 0:
            i = line.split()[0]
            data.append((i, indicator_type(i), direction, source, '', current_date))
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
    current_date = str(datetime.date.today())
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            i = line.split('|')[2].strip()
            data.append((i, indicator_type(i), direction, source, '', current_date))
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
    filter_comments = lambda x: not x[0].startswith('#')
    try:
        for line in ifilter(filter_comments,
                            reader(response.splitlines(), delimiter=';')):
            i = line[0]
            date = line[1].split(' ')[1]
            data.append((i, indicator_type(i), direction, source, '', date))
    except (IndexError, AttributeError):
        pass
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
    current_date = str(datetime.date.today())
    for line in response.splitlines():
        if not line.startswith('#') and len(line) > 0:
            i = line.partition(':')[2].strip()
            data.append((i, indicator_type(i), direction, source, '', current_date))
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


def thresh(input_file, output_file):
    config = ConfigParser.SafeConfigParser(allow_no_value=False)
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        logger.error('Thresher: Could not read combine.cfg.')
        logger.error('HINT: edit combine-example.cfg and save as combine.cfg.')
        return

    plugin_dir = config.get('Thresher', 'plugin_directory')

    logger.info('Loading raw feed data from %s' % input_file)
    with open(input_file, 'rb') as f:
        crop = json.load(f)

    harvest = []

    # TODO: replace with a proper plugin system (cf. #23)
    thresher_map = {'blocklist.de': process_simple_list,
                    'openbl': process_simple_list,
                    'ciarmy': process_simple_list,
                    'rulez': process_rulez,
                    'sans': process_sans,
                    'packetmail': process_packetmail,
                    'autoshun': process_autoshun,
                    'the-haleys': process_haleys,
                    'virbl': process_simple_list,
                    'dragonresearchgroup': process_drg,
                    'malwaregroup': process_malwaregroup,
                    'malc0de': process_simple_list,
                    'file://': process_simple_list}

    # Load the plugins from the plugin directory.
    logger.info('Loading plugins')
    manager = PluginManager()
    manager.setPluginPlaces([plugin_dir])
    manager.collectPlugins()

    # When we have plugins, this hack won't be necessary
    #for type in crop:
    for response in crop:
        # Loop through all the plugins and see which ones have matching names
        for plugin in manager.getAllPlugins():
            logger.info(plugin.plugin_object.get_name())
            logger.info(response[0])
            if plugin.plugin_object.get_name() in response[0]:
                if response[1] == 200:
                    logger.info(response[1])
                    logger.info('Parsing feed from %s' % response[0])
                    harvest += plugin.plugin_object.process_data(response[0], response[2])
                else:  # how to handle non-200 non-404?
                    logger.error('Could not handle %s: %s' % (response[0], response[1]))

    logger.info('Storing parsed data in %s' % output_file)
    with open(output_file, 'wb') as f:
        json.dump(harvest, f, indent=2)


if __name__ == "__main__":
    thresh('harvest.json', 'crop.json')
