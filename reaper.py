import ConfigParser
import grequests
import json
import sys


def exception_handler(request, exception):
    print "Request %r failed: %r" % (request, exception)


def reap(file_name):
    config = ConfigParser.SafeConfigParser(allow_no_value=False)
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        sys.stderr.write('Reaper: Could not read combine.cfg.\n')
        sys.stderr.write('HINT: edit combine-example.cfg and save as combine.cfg.\n')
        return

    inbound_url_file = config.get('Reaper', 'inbound_urls')
    outbound_url_file = config.get('Reaper', 'outbound_urls')

    with open(inbound_url_file, 'rb') as f:
        inbound_urls = [url.rstrip('\n') for url in f.readlines()]
    with open(outbound_url_file, 'rb') as f:
        outbound_urls = [url.rstrip('\n') for url in f.readlines()]
    headers = {'User-Agent': 'harvest.py'}

    sys.stderr.write('Fetching inbound URLs\n')
    reqs = [grequests.get(url, headers=headers) for url in inbound_urls]
    inbound_responses = grequests.map(reqs)
    inbound_harvest = [(response.url, response.status_code, response.text) for response in inbound_responses]

    sys.stderr.write('Fetching outbound URLs\n')
    reqs = [grequests.get(url, headers=headers) for url in outbound_urls]
    outbound_responses = grequests.map(reqs)
    outbound_harvest = [(response.url, response.status_code, response.text) for response in outbound_responses]

    sys.stderr.write('Storing raw feeds in %s\n' % file_name)
    harvest = {'inbound': inbound_harvest, 'outbound': outbound_harvest}

    with open(file_name, 'wb') as f:
        json.dump(harvest, f, indent=2)


if __name__ == "__main__":
    reap('harvest.json')
