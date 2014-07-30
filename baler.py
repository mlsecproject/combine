import csv
import json


def bale_csv(harvest, output_file):
    with open(output_file, 'wb') as csv_file:
        bale_writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        # header row
        bale_writer.writerow(('entity', 'type', 'direction', 'source', 'notes', 'date'))
        bale_writer.writerows(harvest)


def bale(input_file, output_file, output_format):
    with open(input_file, 'rb') as f:
        harvest = json.load(f)

    format_funcs = {'csv': bale_csv}
    format_funcs[output_format](harvest, output_file)


if __name__ == "__main__":
    bale('crop.json', 'harvest.csv', 'csv')
