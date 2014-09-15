import ConfigParser
import grequests
import json
import sys


def exception_handler(request, exception):
    print "Request %r failed: %r" % (request, exception)


def reap(file_name):
    config = ConfigParser.ConfigParser()
    config.read('combine.cfg')

    inbound_url_file = config.get('Reaper', 'inbound_urls')
    outbound_url_file = config.get('Reaper', 'outbound_urls')

    with open(inbound_url_file, 'rb') as f:
        inbound_urls = [url.rstrip('\n') for url in f.readlines()]
    with open(outbound_url_file, 'rb') as f:
        outbound_urls = [url.rstrip('\n') for url in f.readlines()]

    sys.stderr.write('Fetching inbound URLs\n')
    inbound_files=[]
    for url in inbound_urls:
        if url.startswith('file://'):
            inbound_files.append(url.partition('://')[2])
            inbound_urls.remove(url)
    headers = {'User-Agent': 'harvest.py'}
    reqs = [grequests.get(url, headers=headers) for url in inbound_urls]
    inbound_responses = grequests.map(reqs)
    inbound_harvest = [(response.url, response.status_code, response.text) for response in inbound_responses if response]
    for each in inbound_files:
        with open(each,'rb') as f:
            inbound_harvest.append(('file://'+each, '200', f.read()))

    sys.stderr.write('Fetching outbound URLs\n')
    outbound_files=[]
    for url in outbound_urls:
        if url.startswith('file://'):
            outbound_files.append(url.partition('://')[2])
            outbound_urls.remove(url)
    reqs = [grequests.get(url, headers=headers) for url in outbound_urls]
    outbound_responses = grequests.map(reqs)
    outbound_harvest = [(response.url, response.status_code, response.text) for response in outbound_responses if response]
    for each in outbound_files:
        with open(each,'rb') as f:
            outbound_harvest.append(('file://'+each, '200', f.read()))
    
    sys.stderr.write('Storing raw feeds in %s\n' % file_name)
    harvest = {'inbound': inbound_harvest, 'outbound': outbound_harvest}

    with open(file_name, 'wb') as f:
        json.dump(harvest, f, indent=2)


if __name__ == "__main__":
    reap('harvest.json')
