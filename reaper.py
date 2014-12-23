import ConfigParser
import grequests
import json
import sys
from logger import get_logger
import logging


logger = get_logger('reaper')

def exception_handler(request, exception):
    logger.error("Request %r failed: %r" % (request, exception))

def get_feeds(feed_dictonary):
    # Inbound file://
    file_feeds={}
    for label, url in feed_dictonary.iteritems():
        if url.startswith('file://'):
            file_feeds[label] = url.partition('://')[2]
            feed_dictonary.remove(url)

    # Fire requests
    headers = {'User-Agent': 'harvest.py'}
    reqs = [grequests.get(url, headers=headers) for label, url in feed_dictonary.iteritems()]
    responses = grequests.map(reqs, exception_handler=exception_handler)
    
    # Now to build the response array, since there is no way yet to label a 
    # request with grequest, we must search the associated tag by looping the
    # inbound feed dict
    feed_harvest = []
    for response in responses:
        if response:
            for label, url in feed_dictonary.iteritems():
                if url == response.url:
                    feed_harvest.append((label, response.status_code, response.text))
    
    for label, each in file_feeds:
        try:
            with open(each,'rb') as f:
                feed_harvest.append((label, 200, f.read()))
        except IOError as e:
            assert isinstance(logger, logging.Logger)
            logger.error('Reaper: Error while opening "%s" - %s' % (each, e.strerror))

    return feed_harvest

def reap(file_name):
    config = ConfigParser.SafeConfigParser(allow_no_value=False)
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        logger.error('Reaper: Could not read combine.cfg.')
        logger.error('HINT: edit combine-example.cfg and save as combine.cfg.')
        return

    inbound_urls = dict(config.items('feeds.inbound'))
    outbound_urls = dict(config.items('feeds.outbound'))

    logger.info('Fetching inbound URLs')
    inbound_harvest = get_feeds(inbound_urls)

    logger.info('Fetching outbound URLs')
    outbound_harvest = get_feeds(outbound_urls )

    logger.info('Storing raw feeds in %s' % file_name)
    harvest = {'inbound': inbound_harvest, 'outbound': outbound_harvest}

    with open(file_name, 'wb') as f:
        json.dump(harvest, f, indent=2)


if __name__ == "__main__":
    reap('harvest.json')
