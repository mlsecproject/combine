import ConfigParser
import datetime as dt
import gzip
import json
import logging
import os
import re
import requests
import sys
import time
import unicodecsv
import threading
from logger import get_logger
from Queue import Queue

logger = get_logger('baler')


def tiq_output(reg_file, enr_file):
    config = ConfigParser.SafeConfigParser()
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        logger.error('tiq_output: Could not read combine.cfg.')
        logger.error('HINT: edit combine-example.cfg and save as combine.cfg.')
        return

    tiq_dir = os.path.join(config.get('Baler', 'tiq_directory'), 'data')
    today = dt.datetime.today().strftime('%Y%m%d')

    with open(reg_file, 'rb') as f:
        reg_data = json.load(f)

    with open(enr_file, 'rb') as f:
        enr_data = json.load(f)
    logger.info('Preparing tiq directory structure under %s' % tiq_dir)
    if not os.path.isdir(tiq_dir):
        os.makedirs(os.path.join(tiq_dir, 'raw', 'public_inbound'))
        os.makedirs(os.path.join(tiq_dir, 'raw', 'public_outbound'))
        os.makedirs(os.path.join(tiq_dir, 'enriched', 'public_inbound'))
        os.makedirs(os.path.join(tiq_dir, 'enriched', 'public_outbound'))

    inbound_data = [row for row in reg_data if row[2] == 'inbound']
    outbound_data = [row for row in reg_data if row[2] == 'outbound']

    try:
        bale_reg_csvgz(inbound_data, os.path.join(tiq_dir, 'raw', 'public_inbound', today + '.csv.gz'))
        bale_reg_csvgz(outbound_data, os.path.join(tiq_dir, 'raw', 'public_outbound', today + '.csv.gz'))
    except:
        pass

    inbound_data = [row for row in enr_data if row[2] == 'inbound']
    outbound_data = [row for row in enr_data if row[2] == 'outbound']

    try:
        bale_enr_csvgz(inbound_data, os.path.join(tiq_dir, 'enriched', 'public_inbound', today + '.csv.gz'))
        bale_enr_csvgz(outbound_data, os.path.join(tiq_dir, 'enriched', 'public_outbound', today + '.csv.gz'))
    except:
        pass


# oh my god this is such a hack

def bale_reg_csvgz(harvest, output_file):
    """ bale the data as a gziped csv file"""
    logger.info('Output regular data as GZip CSV to %s' % output_file)
    with gzip.open(output_file, 'wb') as csv_file:
        bale_writer = unicodecsv.writer(csv_file, quoting=unicodecsv.QUOTE_ALL)

        # header row
        bale_writer.writerow(('entity', 'type', 'direction', 'source', 'notes', 'date'))
        bale_writer.writerows(harvest)


def bale_reg_csv(harvest, output_file):
    """ bale the data as a csv file"""
    logger.info('Output regular data as CSV to %s' % output_file)
    with open(output_file, 'wb') as csv_file:
        bale_writer = unicodecsv.writer(csv_file, quoting=unicodecsv.QUOTE_ALL)

        # header row
        bale_writer.writerow(('entity', 'type', 'direction', 'source', 'notes', 'date'))
        bale_writer.writerows(harvest)


def bale_enr_csv(harvest, output_file):
    """ output the data as an enriched csv file"""
    logger.info('Output enriched data as CSV to %s' % output_file)
    with open(output_file, 'wb') as csv_file:
        bale_writer = unicodecsv.writer(csv_file, quoting=unicodecsv.QUOTE_ALL)

        # header row
        bale_writer.writerow(('entity', 'type', 'direction', 'source', 'notes', 'date', 'asnumber', 'asname', 'country', 'host', 'rhost'))
        bale_writer.writerows(harvest)


def bale_enr_csvgz(harvest, output_file):
    """ output the data as an enriched gziped csv file"""
    logger.info('Output enriched data as GZip CSV to %s' % output_file)
    with gzip.open(output_file, 'wb') as csv_file:
        bale_writer = unicodecsv.writer(csv_file, quoting=unicodecsv.QUOTE_ALL)

        # header row
        bale_writer.writerow(('entity', 'type', 'direction', 'source', 'notes', 'date', 'asnumber', 'asname', 'country', 'host', 'rhost'))
        bale_writer.writerows(harvest)


def bale_CRITs_indicator(base_url, data, indicator_que):
    """ One thread of adding indicators to CRITs"""
    while not indicator_que.empty():
        indicator = indicator_que.get()
        if indicator[1] == 'IPv4':
            # using the IP API
            url = base_url + 'ips/'
            data['add_indicator'] = "true"
            data['ip'] = indicator[0]
            data['ip_type'] = 'Address - ipv4-addr'
            data['reference'] = indicator[3]
            # getting the source automatically:
            source = re.findall(r'\/\/(.*?)\/', data['reference'])
            if source:
                data['source'] = source[0]
            res = requests.post(url, data=data, verify=False)
            if not res.status_code in [201, 200, 400]:
                logger.info("Issues with adding: %s" % data['ip'])
        elif indicator[1] == "FQDN":
            # using the Domain API
            url = base_url + 'domains/'
            data['add_indicator'] = "true"
            data['domain'] = indicator[0]
            data['reference'] = indicator[3]
            # getting the source automatically:
            source = re.findall(r'\/\/(.*?)\/', data['reference'])
            if source:
                data['source'] = source[0]
            res = requests.post(url, data=data, verify=False)
            if not res.status_code in [201, 200, 400]:
                logger.info("Issues with adding: %s" % data['domain'])
        else:
            logger.info("don't yet know what to do with: %s[%s]" % (indicator[1], indicator[0]))


def bale_CRITs(harvest, filename):
    """ taking the output from combine and pushing it to the CRITs web API"""
    # checking the minimum requirements for parameters
    # it would be nice to have some metadata on the feeds that can be imported in the intel library:
    #   -> confidence
    #   -> type of feed (bot vs spam vs ddos, you get the picture)
    data = {'confidence': 'medium'}
    start_time = time.time()
    config = ConfigParser.SafeConfigParser()
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        logger.error('tiq_output: Could not read combine.cfg.\n')
        logger.error('HINT: edit combine-example.cfg and save as combine.cfg.\n')
        return
    if config.has_option('Baler', 'crits_username'):
        data['username'] = config.get('Baler', 'crits_username')
    else:
        raise 'Please check the combine.cnf file for the crits_username field in the [Baler] section'
    if config.has_option('Baler', 'crits_api_key'):
        data['api_key'] = config.get('Baler', 'crits_api_key')
    else:
        raise 'Please check the combine.cnf file for the crits_api_key field in the [Baler] section'
    if config.has_option('Baler', 'crits_campaign'):
        data['campaign'] = config.get('Baler', 'crits_campaign')
    else:
        logger.info('Lacking a campaign name, we will default to "combine." Errors might ensue if it does not exist in CRITs')
        data['campaign'] = 'combine'
    if config.has_option('Baler', 'crits_url'):
        base_url = config.get('Baler', 'crits_url')
    else:
        raise 'Please check the combine.cnf file for the crits_url field in the [Baler] section'
    if config.has_option('Baler', 'crits_maxThreads'):
        maxThreads = int(config.get('Baler', 'crits_maxThreads'))
    else:
        logger.info('No number of maximum Threads has been given, defaulting to 10')
        maxThreads = 10

    data['source'] = 'Combine'
    data['method'] = 'trawl'

    # initializing the Queue to the list of indicators in the harvest
    ioc_queue = Queue()
    for indicator in harvest:
        ioc_queue.put(indicator)
    total_iocs = ioc_queue.qsize()

    for x in range(maxThreads):
        th = threading.Thread(target=bale_CRITs_indicator, args=(base_url, data, ioc_queue))
        th.start()

    for x in threading.enumerate():
        if x.name == "MainThread":
            continue
        x.join()

    logger.info('Output %d indicators to CRITs using %d threads. Operation tool %d seconds\n' %
                (total_iocs, maxThreads, time.time() - start_time))


def bale(input_file, output_file, output_format, is_regular):
    config = ConfigParser.SafeConfigParser()
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        logger.error('Baler: Could not read combine.cfg.')
        logger.error('HINT: edit combine-example.cfg and save as combine.cfg.')
        return

    logger.info('Reading processed data from %s' % input_file)
    with open(input_file, 'rb') as f:
        harvest = json.load(f, encoding='utf8')

    # TODO: also need plugins here (cf. #23)
    if is_regular:
        format_funcs = {'csv': bale_reg_csv, 'crits': bale_CRITs}
    else:
        format_funcs = {'csv': bale_enr_csv, 'crits': bale_CRITs}
    format_funcs[output_format](harvest, output_file)

if __name__ == "__main__":
    bale('crop.json', 'harvest.csv', 'csv', True)
