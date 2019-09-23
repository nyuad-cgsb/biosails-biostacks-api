import argparse
import requests
import json
import sys
from termcolor import colored, cprint
from pprint import pprint


def search_gencore_modules(name, version=None):
    body = {
        "name": name
    }
    if version:
        body["version"] = version
    uri = 'http://localhost:8082/admin/search/search_modules'
    r = requests.post(uri, json=body)
    json_content = r.content
    modules = json.loads(json_content)
    print('Software: {} is available in the following modules'.format(name))
    for m in modules['modules']:
        print('Module: {}/{} has {}={}'.format(m['name'], m['version'],
                                                        m['dependencies']['name'],
                                                        m['dependencies']['version']))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', '-n',
                        required=True,
                        help='Software name: samtools, bamtools, r, bioconductor. Make sure all packages are in lower case!')
    parser.add_argument('--version', '-v',
                        help='Optiona: Software version (1.0, 2.0, etc)')
    args = parser.parse_args()
    pprint(args)

    search_gencore_modules(args.name)
