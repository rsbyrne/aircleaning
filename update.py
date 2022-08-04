###############################################################################
''''''
###############################################################################


if __name__ != '__main__':
    raise RuntimeError("This script expects to be executed.")


print("Running application code...")


import os

from aircleaning import load, analyse, produce


repodir = os.path.dirname(__file__)
productsdir = os.path.join(repodir, 'products')


produce.multi_cost_analysis()
produce.synoptic()
produce.dashboard()


print("Application code ran successfully.")


###############################################################################
###############################################################################
