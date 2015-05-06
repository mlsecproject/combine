#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import json
import logging
import multiprocessing as mp
from logging import getLogger

import requests
from logbook.compat import redirect_logging
from yapsy.PluginManager import PluginManager


redirect_logging()

# logging.getLogger('yapsy').setLevel(logging.DEBUG)
logging.getLogger('yapsy').setLevel(logging.INFO)
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = getLogger('reaper')

# Setting the User-Agent to something spiffy
headers = {'User-Agent': 'MLSecProject-Combine/0.1.2 (+https://github.com/mlsecproject/combine)'}


def get_file(url, q, optional_headers=None):
    global headers
    h = headers
    r = None
    if optional_headers:
        h.update(optional_headers)
    try:
        r = requests.get(url, headers=h, timeout=7.0)
    except Exception as e:
        logger.error("Requests Error: %s" % str(e))
    q.put(r)


def reap(file_name):
    config = ConfigParser.SafeConfigParser(allow_no_value=False)
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        logger.error('Reaper: Could not read combine.cfg.')
        logger.error('HINT: edit combine-example.cfg and save as combine.cfg.')
        return

    plugin_dir = config.get('Reaper', 'plugin_directory')
    if plugin_dir is None or plugin_dir == '':
        logger.error("Reaper: Couldn't find plugins for processing")
        return

    logger.info('Loading Plugins')
    # Load the plugins from the plugin directory.
    manager = PluginManager()
    manager.setPluginPlaces([plugin_dir])
    manager.collectPlugins()

    reqs = []
    files = []

    q = mp.Queue()
    urlcount = 0
    QUEUELIMIT = 32767
    # Loop through all the plugins and gather the URLs
    for plugin in manager.getAllPlugins():
        logger.info('Processing: ' + plugin.plugin_object.get_name())
        o_headers = None
        try:
            o_headers = plugin.plugin_object.get_headers()
        except Exception as e:
            pass  # because we don't care if this isn't implemented in plugins
        for url in plugin.plugin_object.get_URLs():
            if url.startswith('file://'):
                files.append(url.partition('://')[2])
            else:
                try:
                    # There is a limit to how many things you can cram in a queue
                    if urlcount <= QUEUELIMIT:
                        urlcount += 1
                        p = mp.Process(target=get_file, args=(url, q, o_headers))
                        p.start()
                        reqs.append(p)
                        logger.debug('Added: ' + url)
                except Exception as e:
                    pass

    responses = []
    while urlcount > 0:
        urlcount -= 1
        try:
            r = q.get(True, 10)
            if r is not None:
                responses.append(r)
        except Exception as e:
            logger.error('Reaper: Queue Error "%s"' % str(e))

    for p in reqs:
        try:
            p.join(1)
        except Exception as e:
            logger.error('Reaper: Thread Join Error "%s"' % str(e))

    harvest = [(response.url, response.status_code, response.text) for response in responses if response]

    logger.info('Storing raw feeds in %s' % file_name)
    with open(file_name, 'wb') as f:
        json.dump(harvest, f, indent=2)


def main():
    reap('harvest.json')

if __name__ == "__main__":
    main()
