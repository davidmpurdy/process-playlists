###
# Very basic command line interface to process an EVT file
###

import sys
from process_log import process_file

source_file = sys.argv[1]

process_file (source_file)