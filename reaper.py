import ConfigParser
import grequests
import json
import sys
import logging
from yapsy.PluginManager import PluginManager
from logbook.compat import redirect_logging
from logging import getLogger

#requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.SecurityWarning)

redirect_logging()

logger = getLogger('reaper')
logging.getLogger('yapsy').setLevel(logging.DEBUG)

def exception_handler(request, exception):
    logger.error("Request %r failed: %r" % (request, exception))

def reap(file_name):
    config = ConfigParser.SafeConfigParser(allow_no_value=False)
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        logger.error('Reaper: Could not read combine.cfg.')
        logger.error('HINT: edit combine-example.cfg and save as combine.cfg.')
        return

    inbound_url_file = config.get('Reaper', 'inbound_urls')
    outbound_url_file = config.get('Reaper', 'outbound_urls')
    plugin_dir = config.get('Reaper', 'plugin_directory')

    try:
        with open(inbound_url_file, 'rb') as f:
    	    inbound_urls = [url.rstrip('\n') for url in f.readlines()]
    except EnvironmentError as e:
        logger.error('Reaper: Error while opening "%s" - %s' % (inbound_url_file, e.strerror))
        return

    try:
        with open(outbound_url_file, 'rb') as f:
            outbound_urls = [url.rstrip('\n') for url in f.readlines()]
    except EnvironmentError as e:
        logger.error('Reaper: Error while opening "%s" - %s' % (outbound_url_file, e.strerror))
        return

    ## Setting the User-Agent to something spiffy
    headers = {'User-Agent': 'MLSecProject-Combine/0.1.2 (+https://github.com/mlsecproject/combine)'}

    logger.info('Loading Plugins')
    # Load the plugins from the plugin directory.
    manager = PluginManager()
    manager.setPluginPlaces([plugin_dir])
    manager.collectPlugins()

    #inbound_files = []
    #inbound_reqs = []
    #outbound_files = []
    #outbound_reqs = []
    #hash_files = []
    #hash_reqs = []
    reqs = []
    files = []
    
    # Loop through all the plugins and gather the URLs
    for plugin in manager.getAllPlugins():
        direction = plugin.plugin_object.get_direction()
        logger.info(direction)
        for url in plugin.plugin_object.get_URLs():
            if url.startswith('file://'):
                files.append(url.partition('://')[2])
            else:
                reqs.append(grequests.get(url, headers=headers))
            #if direction == 'inbound':
            #    if url.startswith('file://'):
            #        inbound_files.append(url.partition('://')[2])
            #    else:
            #        inbound_reqs.append(grequests.get(url, headers=headers))
            #elif direction == 'outbound':
            #    logger.info(url)
            #    if url.startswith('file://'):
            #        outbound_files.append(url.partition('://')[2])
            #    else:
            #        outbound_reqs.append(grequests.get(url, headers=headers, verify=False))
            #elif direction == 'hash':
            #    if url.startswith('file://'):
            #        hash_files.append(url.partition('://')[2])
            #    else:
            #        hash_reqs.append(grequests.get(url, headers=headers))

    #inbound_responses = grequests.map(inbound_reqs, exception_handler=exception_handler)
    #outbound_responses = grequests.map(outbound_reqs, exception_handler=exception_handler)
    #hash_responses = grequests.map(hash_reqs, exception_handler=exception_handler)
    responses = grequests.map(reqs, exception_handler=exception_handler)

    #inbound_harvest = [(response.url, response.status_code, response.text) for response in inbound_responses if response]
    #outbound_harvest = [(response.url, response.status_code, response.text) for response in outbound_responses if response]
    #hash_harvest = [(response.url, response.status_code, response.text) for response in hash_responses if response]
    harvest = [(response.url, response.status_code, response.text) for response in responses if response]

    #for each in inbound_files:
    #    try:
    #        with open(each,'rb') as f:
    #            inbound_harvest.append(('file://'+each, 200, f.read()))
    #    except IOError as e:
    #        assert isinstance(logger, logging.Logger)
    #        logger.error('Reaper: Error while opening "%s" - %s' % (each, e.strerror))
    #for each in outbound_files:
    #    try:
    #        with open(each,'rb') as f:
    #            outbound_harvest.append(('file://'+each, 200, f.read()))
    #    except IOError as e:
    #        assert isinstance(logger, logging.Logger)
    #        logger.error('Reaper: Error while opening "%s" - %s' % (each, e.strerror))
    #for each in hash_files:
    #    try:
    #        with open(each,'rb') as f:
    #            hash_harvest.append(('file://'+each, 200, f.read()))
    #    except IOError as e:
    #        assert isinstance(logger, logging.Logger)
    #        logger.error('Reaper: Error while opening "%s" - %s' % (each, e.strerror))
            
    for each in files:
        try:
            with open(each,'rb') as f:
                hash_harvest.append(('file://'+each, 200, f.read()))
        except IOError as e:
            assert isinstance(logger, logging.Logger)
            logger.error('Reaper: Error while opening "%s" - %s' % (each, e.strerror))
            
    logger.info('Storing raw feeds in %s' % file_name)
    #harvest = {'inbound': inbound_harvest, 'outbound': outbound_harvest, 'hash': hash_harvest}

    with open(file_name, 'wb') as f:
        json.dump(harvest, f, indent=2)


if __name__ == "__main__":
    reap('harvest.json')
