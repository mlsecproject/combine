import json
import grequests


def exception_handler(request, exception):
    print "Request %r failed: %r" % (request, exception)


def reap(file_name):
    with open('urls.txt', 'rb') as f:
        urls = [url.rstrip('\n') for url in f.readlines()]
    headers = {'User-Agent': 'harvest.py'}

    reqs = [grequests.get(url, headers=headers) for url in urls]
    responses = grequests.map(reqs)
    harvest = [(response.url, response.status_code, response.text) for response in responses]

    with open(file_name, 'wb') as f:
        json.dump(harvest, f, indent=2)


if __name__ == "__main__":
    reap('harvest.json')
