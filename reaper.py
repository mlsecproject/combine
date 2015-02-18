import ConfigParser
import json
import sys
import logging
import requests
import multiprocessing as mp
from yapsy.PluginManager import PluginManager
from logbook.compat import redirect_logging
from logging import getLogger
import uniaccept

redirect_logging()

#logging.getLogger('yapsy').setLevel(logging.DEBUG)
logging.getLogger('yapsy').setLevel(logging.INFO)
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = getLogger('reaper')

## Setting the User-Agent to something spiffy
headers = {'User-Agent': 'MLSecProject-Combine/0.1.2 (+https://github.com/mlsecproject/combine)'}

def get_file(url, q):
    global headers
    r = requests.get(url)
    q.put(r)

def reap(file_name):
    config = ConfigParser.SafeConfigParser(allow_no_value=False)
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        logger.error('Reaper: Could not read combine.cfg.')
        logger.error('HINT: edit combine-example.cfg and save as combine.cfg.')
        return

    plugin_dir = config.get('Reaper', 'plugin_directory')
    if plugin_dir == None or plugin_dir == '':
        logger.error("Thresher: Couldn't find plugins for processing")
        return


    logger.info('Loading Plugins')
    # Load the plugins from the plugin directory.
    manager = PluginManager()
    manager.setPluginPlaces([plugin_dir])
    manager.collectPlugins()

    reqs = []
    files = []
    queues = [] 
    # Loop through all the plugins and gather the URLs
    for plugin in manager.getAllPlugins():
        logger.info('Processing: ' + plugin.plugin_object.get_name())
        for url in plugin.plugin_object.get_URLs():
            if url.startswith('file://'):
                files.append(url.partition('://')[2])
            else:
                try:
                    q = mp.Queue()
                    p = mp.Process(target=get_file, args=(url, q))
                    p.start()
                    reqs.append(p)
                    queues.append(q)
                except Exception as e:
                    pass

    responses = [q.get() for q in queues]
    [p.join() for r in reqs]
    harvest = [(response.url, response.status_code, response.text) for response in responses if response]
    for each in files:
        try:
            with open(each,'rb') as f:
                hash_harvest.append(('file://'+each, 200, f.read()))
        except IOError as e:
            assert isinstance(logger, logging.Logger)
            logger.error('Reaper: Error while opening "%s" - %s' % (each, e.strerror))
            
    logger.info('Storing raw feeds in %s' % file_name)
    with open(file_name, 'wb') as f:
        json.dump(harvest, f, indent=2)


if __name__ == "__main__":
    reap('harvest.json')
