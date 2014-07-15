import argparse
import json
import grequests


def exception_handler(request, exception):
    print "Request %r failed: %r" % (request, exception)


def main():
    with open('urls.txt', 'rb') as f:
        urls = f.readlines()
    headers = {'User-Agent': 'harvest.py'}

    reqs = [grequests.get(url, headers=headers) for url in urls]
    grequests.map(reqs, exception_handler=exception_handler)
    harvest = [req.text for req in reqs]

    with open('harvest.json', 'wb') as f:
        json.dump(harvest, f)

if __name__ == "__main__":
    main()
