###############################################################################
''''''
###############################################################################


# if __name__ != '__main__':
#     raise RuntimeError("This script expects to be executed.")
# raise Exception

print("Running application code...")


import os
import hashlib
import sys
import argparse

from . import load, analyse, produce


parser = argparse.ArgumentParser()
parser.add_argument("-f", '--force', help="Force execution", action='store_true')
args = parser.parse_args()


repodir = os.path.dirname(__file__)
productsdir = os.path.join(repodir, 'products')


def get_token():
    m = hashlib.sha256()
    for dsetname in ('main', 'volume', 'quality', 'parameters'):
        data = getattr(load, f'pull_{dsetname}_data')()
        strn = data.to_string()
        m.update(strn.encode())
    return m.digest()


token = get_token()
with open('token.txt', mode='rb') as file:
    loadtoken = file.read()


def execute():
    produce.multi_cost_analysis()
    produce.synoptic()
    produce.decision_tool()
    produce.overview()


if token == loadtoken:
    if args.force:
        print("Forcing execution: running workflow...")
        execute()
    else:
        print("No changes detected: skipping workflow...")
else:
    print("Changes detected: running workflow...")
    execute()
    with open('token.txt', mode='wb') as file:
        file.write(token)

print("Application code ran successfully.")


###############################################################################
###############################################################################
