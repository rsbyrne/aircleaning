###############################################################################
''''''
###############################################################################


if __name__ != '__main__':
    raise RuntimeError("This script expects to be executed.")


import os

from aircleaning import load, analyse, produce


repodir = os.path.dirname(__file__)
productsdir = os.path.join(repodir, 'products')


produce.multi_cost_analysis()


###############################################################################
###############################################################################
