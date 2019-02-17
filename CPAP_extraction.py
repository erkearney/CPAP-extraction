import argparse             # For command line arguments
import os                   # For file IO
from pathlib import Path    # For validating file paths

import decorators           # For debugging, see the decorators.py file

def hello_world():
    print("Hello world!")
    return 0

# This function is for testing only, it will be deleted
def copy_file(source, destination): 
    source = Path(source[0])
    if not source.is_file():
        print("ERROR: source file {} not found!".format(source))
        exit()

    destination = Path(destination[0])
    if not os.path.isdir(destination):
        print("ERROR: destination directory {} not found!".format(destination))
        exit()

    outfile = '{}/{}_extracted'.format(destination, source)


    with open(source, 'rb') as input:
        with open(outfile, 'wb') as output:
            for line in input:
                output.write(line)

    if args.v:
        print('Done, the original file is size {}, '
              'The extracted file is size {}'
              .format(os.path.getsize(source), os.path.getsize(outfile)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CPAP_data_extraction')
    parser.add_argument('source', nargs=1, help='path to CPAP data')
    parser.add_argument('destination', nargs=1, help='path to place extacted \
    data')
    parser.add_argument('-v', action='store_true', help='be verbose')

    args = parser.parse_args()

    copy_file(args.source, args.destination)
