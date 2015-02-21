import ConfigParser
import bs4
import datetime
import feedparser
import json
import re
import sys
import logging
from csv import reader
from itertools import ifilter
from yapsy.PluginManager import PluginManager
from logbook.compat import redirect_logging
from logging import getLogger

redirect_logging()

logging.getLogger('yapsy').setLevel(logging.INFO)
logger = getLogger('thresher')

def thresh(input_file, output_file):
    config = ConfigParser.SafeConfigParser(allow_no_value=False)
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        logger.error('Thresher: Could not read combine.cfg.')
        logger.error('HINT: edit combine-example.cfg and save as combine.cfg.')
        return

    plugin_dir = config.get('Thresher', 'plugin_directory')
    if plugin_dir == None or plugin_dir == '':
        logger.error("Thresher: Couldn't find plugins for processing")
        return

    logger.info('Loading raw feed data from %s' % input_file)
    with open(input_file, 'rb') as f:
        crop = json.load(f)

    harvest = []

    # Load the plugins from the plugin directory.
    logger.info('Loading plugins')
    manager = PluginManager()
    manager.setPluginPlaces([plugin_dir])
    manager.collectPlugins()

    # When we have plugins, this hack won't be necessary
    for response in crop:
        # Loop through all the plugins and see which ones have matching names
        for plugin in manager.getAllPlugins():
            if plugin.plugin_object.get_name() in response[0]:
                if response[1] == 200:
                    logger.info('Parsing feed from %s' % response[0])
                    harvest += plugin.plugin_object.process_data(response[0], response[2])
                else:  # how to handle non-200 non-404?
                    logger.error('Could not handle %s: %s' % (response[0], response[1]))

    logger.info('Storing parsed data in %s' % output_file)
    with open(output_file, 'wb') as f:
        json.dump(harvest, f, indent=2)


if __name__ == "__main__":
    thresh('harvest.json', 'crop.json')
