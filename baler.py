import ConfigParser
import csv
import datetime as dt
import gzip
import json
import os
import sys
import requests
import time
import re
from Queue import Queue
import threading



def tiq_output(reg_file, enr_file):
    config = ConfigParser.SafeConfigParser()
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        sys.stderr.write('tiq_output: Could not read combine.cfg.\n')
        sys.stderr.write('HINT: edit combine-example.cfg and save as combine.cfg.\n')
        return

    tiq_dir = os.path.join(config.get('Baler', 'tiq_directory'), 'data')
    today = dt.datetime.today().strftime('%Y%m%d')

    with open(reg_file, 'rb') as f:
        reg_data = json.load(f)

    with open(enr_file, 'rb') as f:
        enr_data = json.load(f)

    sys.stderr.write('Preparing tiq directory structure under %s\n' % tiq_dir)
    if not os.path.isdir(tiq_dir):
        os.makedirs(os.path.join(tiq_dir, 'raw', 'public_inbound'))
        os.makedirs(os.path.join(tiq_dir, 'raw', 'public_outbound'))
        os.makedirs(os.path.join(tiq_dir, 'enriched', 'public_inbound'))
        os.makedirs(os.path.join(tiq_dir, 'enriched', 'public_outbound'))

    inbound_data = [row for row in reg_data if row[2] == 'inbound']
    outbound_data = [row for row in reg_data if row[2] == 'outbound']

    try:
        bale_reg_csvgz(inbound_data, os.path.join(tiq_dir, 'raw', 'public_inbound', today+'.csv.gz'))
        bale_reg_csvgz(outbound_data, os.path.join(tiq_dir, 'raw', 'public_outbound', today+'.csv.gz'))
    except:
        pass

    inbound_data = [row for row in enr_data if row[2] == 'inbound']
    outbound_data = [row for row in enr_data if row[2] == 'outbound']

    try:
        bale_enr_csvgz(inbound_data, os.path.join(tiq_dir, 'enriched', 'public_inbound', today+'.csv.gz'))
        bale_enr_csvgz(outbound_data, os.path.join(tiq_dir, 'enriched', 'public_outbound', today+'.csv.gz'))
    except:
        pass


# oh my god this is such a hack

def bale_reg_csvgz(harvest, output_file):
    """ bale the data as a gziped csv file"""
    sys.stderr.write('Output regular data as GZip CSV to %s\n' % output_file)
    with gzip.open(output_file, 'wb') as csv_file:
        bale_writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        # header row
        bale_writer.writerow(('entity', 'type', 'direction', 'source', 'notes', 'date'))
        bale_writer.writerows(harvest)


def bale_reg_csv(harvest, output_file):
    """ bale the data as a csv file"""
    sys.stderr.write('Output regular data as CSV to %s\n' % output_file)
    with open(output_file, 'wb') as csv_file:
        bale_writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        # header row
        bale_writer.writerow(('entity', 'type', 'direction', 'source', 'notes', 'date'))
        bale_writer.writerows(harvest)


def bale_enr_csv(harvest, output_file):
    """ output the data as an enriched csv file"""
    sys.stderr.write('Output enriched data as CSV to %s\n' % output_file)
    with open(output_file, 'wb') as csv_file:
        bale_writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        # header row
        bale_writer.writerow(('entity', 'type', 'direction', 'source', 'notes', 'date', 'asnumber', 'asname', 'country', 'host', 'rhost'))
        bale_writer.writerows(harvest)

def bale_enr_csvgz(harvest, output_file):
    """ output the data as an enriched gziped csv file"""
    sys.stderr.write('Output enriched data as GZip CSV to %s\n' % output_file)
    with gzip.open(output_file, 'wb') as csv_file:
        bale_writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        # header row
        bale_writer.writerow(('entity', 'type', 'direction', 'source', 'notes', 'date', 'asnumber', 'asname', 'country', 'host', 'rhost'))
        bale_writer.writerows(harvest)

def bale_CRITs_indicator(base_url,data,indicator_que):
    """ One thread of adding indicators to CRITs"""
    while not indicator_que.empty():
        indicator=indicator_que.get()
        #print indicator
        if indicator[1] == 'IPv4':
            # using the IP API
            url=base_url+'ips/'
            data['add_indicator']="true"
            data['ip']=indicator[0]
            data['ip_type']='Address - ipv4-addr'
            data['reference']=indicator[3]
            # getting the source automatically:  
            source=re.findall(r'\/\/(.*?)\/',data['reference'])
            if source:
                data['source']=source[0]
            res = requests.post(url,data=data,verify=False)
            if not res.status_code in [201,200]:
                sys.stderr.write("Issues with adding: %s" % data['ip'])
                
        elif indicator[1] == "FQDN":
            # using the Domain API
            url=base_url+'domains/'
            data['add_indicator']="true"
            data['domain']=indicator[0]
            data['reference']=indicator[3]
            # getting the source automatically:
            source=re.findall(r'\/\/(.*?)\/',data['reference'])
            if source:
                data['source']=source[0]
            res = requests.post(url,data=data,verify=False)
            if not res.status_code in [201,200]:
                sys.stderr.write("Issues with adding: %s" % data['domain'])
        else:
            sys.stderr.write("don't yet know what to do with: %s[%s]" % (indicator[1],indicator[0]))

def bale_CRITs_multi(harvest,filename):
    """ taking the output from combine and pushing it to the CRITs web API
    paul@linux-67o4:~/Documents/dev/combine> time python combine.py -t crits
Fetching inbound URLs
Fetching outbound URLs
Storing raw feeds in harvest.json
Loading raw feed data from harvest.json
Evaluating http://www.projecthoneypot.org/list_of_ips.php?rss=1
Parsing feed from http://www.projecthoneypot.org/list_of_ips.php?rss=1
Parsing feed from http://malc0de.com/bl/IP_Blacklist.txt
Storing parsed data in crop.json
Reading processed data from crop.json
0.369317 reading configs
0.369623 initializing queue
0.372198 starting threads
6.461888 finished threads

real    1m10.674s
user    0m5.804s
sys     0m0.683s
"""
    # checking the minimum requirements for parameters
    # it would be nice to have some metadata on the feeds that can be imported in the intel library:
    #   -> confidence
    #   -> type of feed (bot vs spam vs ddos, you get the picture)
    data={'confidence':'medium'}
    start=time.time()
    print time.time(),"reading configs"
    config = ConfigParser.SafeConfigParser()
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        sys.stderr.write('tiq_output: Could not read combine.cfg.\n')
        sys.stderr.write('HINT: edit combine-example.cfg and save as combine.cfg.\n')
        return
    if config.has_option('Baler','username'):
        data['username']=config.get('Baler', 'username')
    else:
        raise 'Please check the combine.cnf file for the username field in the [Baler] section'
    if config.has_option('Baler','api_key'):
        data['api_key']=config.get('Baler', 'api_key')
    else:
        raise 'Please check the combine.cnf file for the api_key field in the [Baler] section'
    if config.has_option('Baler','campaign'):
        data['campaign']=config.get('Baler', 'campaign')
    else:
        sys.stderr.write('Lacking a campaign name, we will default to "combine." Errors might ensue if it does not exist in CRITs')
        data['campaign']='combine'
    if config.has_option('Baler','url'):
        base_url=config.get('Baler','url')
    else:
        raise 'Please check the combine.cnf file for the url field in the [Baler] section'
    # instituting some counts for less verbose output
    data['source']='Combine'
    data['method']='trawl'
    
    print time.time(),"initializing queue"
    # initializing the Queue to the list of indicators in the harvest
    ioc_queue=Queue()
    for indicator in harvest:
        ioc_queue.put(indicator)
        
    print time.time(),"starting threads"
    # setting the number of maximum concomittent threads - if it works, to be read from the config file
    maxThreads=10
    for x in range(maxThreads):
        th=threading.Thread(target=bale_CRITs_indicator, args=(base_url,data,ioc_queue))
        th.start()
        

    for x in threading.enumerate():
        if x.name=="MainThread": 
            continue
        x.join()
    
    print "\n\n",time.time(),"done in ",time.time()-start," seconds"
    
def bale_CRITs_single(harvest,filename):
    """ taking the output from combine and pushing it to the CRITs web API
    paul@linux-67o4:~/Documents/dev/combine> time python combine.py -t crits
Fetching inbound URLs
Fetching outbound URLs
Storing raw feeds in harvest.json
Loading raw feed data from harvest.json
Evaluating http://www.projecthoneypot.org/list_of_ips.php?rss=1
Parsing feed from http://www.projecthoneypot.org/list_of_ips.php?rss=1
Parsing feed from http://malc0de.com/bl/IP_Blacklist.txt
Storing parsed data in crop.json
Reading processed data from crop.json
successfully added 1271 IP addresses and 0 domainsmake sure you have the following sources in CRITs: [u'www.projecthoneypot.org', u'malc0de.com']

real    1m18.975s
user    0m6.163s
sys     0m0.627s

    """
    # checking the minimum requirements for parameters
    # it would be nice to have some metadata on the feeds that can be imported in the intel library:
    #   -> confidence
    #   -> type of feed (bot vs spam vs ddos, you get the picture)
    start=time.time()
    print time.time(),"reading configs"
    data={'confidence':'medium'}
    config = ConfigParser.SafeConfigParser()
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        sys.stderr.write('tiq_output: Could not read combine.cfg.\n')
        sys.stderr.write('HINT: edit combine-example.cfg and save as combine.cfg.\n')
        return
    if config.has_option('Baler','username'):
        data['username']=config.get('Baler', 'username')
    else:
        raise 'Please check the combine.cnf file for the username field in the [Baler] section'
    if config.has_option('Baler','api_key'):
        data['api_key']=config.get('Baler', 'api_key')
    else:
        raise 'Please check the combine.cnf file for the api_key field in the [Baler] section'
    if config.has_option('Baler','campaign'):
        data['campaign']=config.get('Baler', 'campaign')
    else:
        sys.stderr.write('Lacking a campaign name, we will default to "combine." Errors might ensue if it does not exist in CRITs')
        data['campaign']='combine'
    if config.has_option('Baler','url'):
        base_url=config.get('Baler','url')
    else:
        raise 'Please check the combine.cnf file for the url field in the [Baler] section'
    # instituting some counts for less verbose output
    data['source']='Combine'
    data['method']='trawl'
    domain_count=0
    ip_count=0
    sources=[]
    print time.time(),"going through list"
    for indicator in harvest:
        if indicator[1] == 'IPv4':
            # using the IP API
            url=base_url+'ips/'
            data['add_indicator']="true"
            data['ip']=indicator[0]
            data['ip_type']='Address - ipv4-addr'
            data['reference']=indicator[3]
            # getting the source automatically:  
            source=re.findall(r'\/\/(.*?)\/',data['reference'])
            if source:
                data['source']=source[0]
                if not data['source'] in sources:
                    sources.append(data['source'])
            res = requests.post(url,data=data,verify=False)
            if res.status_code == 201 or res.status_code == 200:
                ip_count+=1
            else:
                sys.stderr.write("Issues with adding: %s" % data['ip'])
                sys.stderr.write(res.text)
                print res.status_code
        elif indicator[1] == "FQDN":
            # using the Domain API
            url=base_url+'domains/'
            data['add_indicator']="true"
            data['domain']=indicator[0]
            data['reference']=indicator[3]
            # getting the source automatically:
            source=re.findall(r'\/\/(.*?)\/',data['reference'])
            if source:
                data['source']=source[0]
                if not data['source'] in sources:
                    sources.append(data['source'])
            res = requests.post(url,data=data,verify=False)
            if not res.status_code == 201 or res.status_code == 200:
                domain_count+=1
            else:
                sys.stderr.write("Issues with adding: %s" % data['domain'])
                sys.stderr.write(res.text)
                sys.stderr.write(res.status_code)
        else:
            sys.stderr.write("don't yet know what to do with: %s[%s]" % (indicator[1],indicator[0]))
    sys.stderr.write("successfully added %d IP addresses and %d domains" % (ip_count, domain_count))
    print "\n\n",time.time(),"done in ",time.time()-start," seconds"
    print "make sure you have the following sources in CRITs:",sources
    
def bale_CRITs(harvest,filename):
    print time.time(),"*** trying single thread***"
    bale_CRITs_single(harvest,filename)
    print time.time(),"*** trying multi thread***"
    bale_CRITs_multi(harvest,filename)
    
def bale(input_file, output_file, output_format, is_regular):
    config = ConfigParser.SafeConfigParser()
    cfg_success = config.read('combine.cfg')
    if not cfg_success:
        sys.stderr.write('Baler: Could not read combine.cfg.\n')
        sys.stderr.write('HINT: edit combine-example.cfg and save as combine.cfg.\n')
        return

    sys.stderr.write('Reading processed data from %s\n' % input_file)
    with open(input_file, 'rb') as f:
        harvest = json.load(f)

    # TODO: also need plugins here (cf. #23)
    if is_regular:
        format_funcs = {'csv': bale_reg_csv,'crits':bale_CRITs}
    else:
        format_funcs = {'csv': bale_enr_csv,'crits':bale_CRITs}
    format_funcs[output_format](harvest, output_file)

if __name__ == "__main__":
    bale('crop.json', 'harvest.csv', 'csv', True)
