import ConfigParser
import csv
import datetime
import gzip
import json
import os


def tiq_output(reg_file, enr_file):
    config = ConfigParser.ConfigParser()
    config.read('combine.cfg')
    tiq_dir = os.path.join(config.get('Baler', 'tiq_directory'), 'data')
    today = datetime.today().strftime('%Y%m%d')

    with open(reg_file, 'rb') as f:
        reg_data = json.load(f)

    with open(enr_file, 'rb') as f:
        enr_data = json.load(f)

    if not os.path.isdir(tiq_dir):
        os.makedirs(os.path.join(tiq_dir, 'raw', 'public_inbound'))
        os.makedirs(os.path.join(tiq_dir, 'raw', 'public_inbound'))
        os.makedirs(os.path.join(tiq_dir, 'enriched', 'public_outbound'))
        os.makedirs(os.path.join(tiq_dir, 'enriched', 'public_outbound'))

    inbound_data = [row for row in reg_data if row['direction'] == 'inbound']
    outbound_data = [row for row in reg_data if row['direction'] == 'outbound']

    bale_reg_csvgz(inbound_data, os.path.join(tiq_dir, 'raw', 'public_inbound', today+'.csv.gz'))
    bale_reg_csvgz(outbound_data, os.path.join(tiq_dir, 'raw', 'public_outbound', today+'.csv.gz'))

    inbound_data = [row for row in enr_data if row['direction'] == 'inbound']
    outbound_data = [row for row in enr_data if row['direction'] == 'outbound']

    bale_enr_csvgz(inbound_data, os.path.join(tiq_dir, 'enriched', 'public_inbound', today+'.csv.gz'))
    bale_enr_csvgz(outbound_data, os.path.join(tiq_dir, 'enriched', 'public_outbound', today+'.csv.gz'))


# oh my god this is such a hack

def bale_reg_csvgz(harvest, output_file):
    with gzip.open(output_file, 'wb') as csv_file:
        bale_writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        # header row
        bale_writer.writerow(('entity', 'type', 'direction', 'source', 'notes', 'date'))
        bale_writer.writerows(harvest)


def bale_reg_csv(harvest, output_file):
    with open(output_file, 'wb') as csv_file:
        bale_writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        # header row
        bale_writer.writerow(('entity', 'type', 'direction', 'source', 'notes', 'date'))
        bale_writer.writerows(harvest)


def bale_enr_csv(harvest, output_file):
    with open(output_file, 'wb') as csv_file:
        bale_writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        # header row
        bale_writer.writerow(('entity', 'type', 'direction', 'source', 'notes', 'date', 'asnumber', 'asname', 'country', 'host', 'rhost'))
        bale_writer.writerows(harvest)


def bale_enr_csvgz(harvest, output_file):
    with gzip.open(output_file, 'wb') as csv_file:
        bale_writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        # header row
        bale_writer.writerow(('entity', 'type', 'direction', 'source', 'notes', 'date', 'asnumber', 'asname', 'country', 'host', 'rhost'))
        bale_writer.writerows(harvest)


def bale(input_file, output_file, output_format):
    with open(input_file, 'rb') as f:
        harvest = json.load(f)

    # TODO: also need plugins here (cf. #23)
    format_funcs = {'csv': bale_reg_csv}
    format_funcs[output_format](harvest, output_file)


if __name__ == "__main__":
    bale('crop.json', 'harvest.csv', 'csv')
