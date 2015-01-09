import ConfigParser
import grequests
import json
import sys
from logger import get_logger
import logging


logger = get_logger('reaper')

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

    logger.info('Fetching inbound URLs')
    inbound_files=[]
    for url in inbound_urls:
        if url.startswith('file://'):
            inbound_files.append(url.partition('://')[2])
            inbound_urls.remove(url)
    reqs = [grequests.get(url, headers=headers) for url in inbound_urls]
    inbound_responses = grequests.map(reqs, exception_handler=exception_handler)
    inbound_harvest = [(response.url, response.status_code, response.text) for response in inbound_responses if response]
    for each in inbound_files:
        try:
            with open(each,'rb') as f:
                inbound_harvest.append(('file://'+each, 200, f.read()))
        except IOError as e:
            assert isinstance(logger, logging.Logger)
            logger.error('Reaper: Error while opening "%s" - %s' % (each, e.strerror))

    logger.info('Fetching outbound URLs')
    outbound_files=[]
    for url in outbound_urls:
        if url.startswith('file://'):
            outbound_files.append(url.partition('://')[2])
            outbound_urls.remove(url)
    reqs = [grequests.get(url, headers=headers) for url in outbound_urls]
    outbound_responses = grequests.map(reqs, exception_handler=exception_handler)
    outbound_harvest = [(response.url, response.status_code, response.text) for response in outbound_responses if response]
    for each in outbound_files:
        try:
            with open(each,'rb') as f:
                outbound_harvest.append(('file://'+each, 200, f.read()))
        except IOError as e:
            assert isinstance(logger, logging.Logger)
            logger.error('Reaper: Error while opening "%s" - %s' % (each, e.strerror))

    logger.info('Storing raw feeds in %s' % file_name)
    harvest = {'inbound': inbound_harvest, 'outbound': outbound_harvest}

    with open(file_name, 'wb') as f:
        json.dump(harvest, f, indent=2)


if __name__ == "__main__":
    reap('harvest.json')
