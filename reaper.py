import argparse
import json
import requests


def main():
    harvest = []
    with open('urls.txt', 'rb') as f:
        urls = f.readlines()

    headers = {'User-Agent': 'harvest.py'}
    for url in urls:
        r = requests.get(url, headers=headers)
        harvest.append((url, r.text))

    with open('harvest.json', 'wb') as f:
        json.dump(harvest, f)

if __name__ == "__main__":
    main()
