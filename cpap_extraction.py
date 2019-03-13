'''
This module will take raw CPAP data as an input, and export it to JSON as an
output.

Example
-------
    $ python cpap_extraction.py 38611.000 .

Extracts the raw CPAP data from 38611.000 to a new file called 38611.json

Attributes
----------
source : path
    The source data file(s) to be extracted

destination : path
    The directory to place the extracted files

verbose : bool
'''
import argparse             # For command line arguments
import sys                  # Fir command line arguments
import os                   # For file IO
import decorators           # For debugging, see the decorators.py file


def setup_args():
    '''
    Sets up command-line arguments

    Attributes
    ----------
    source : path
        The source data file(s) to be extracted

    destination : path
        The directory to place the extracted files

    verbose : Boolean
        If True, tell the user how long the extraction took, how big the source
        file(s) were, and how big each extracted file(s) is.

    parser : ArgumentParser
        See https://docs.python.org/2/library/argparse.html

    args : Parsed Arguments
    '''
    global source
    global destination
    global verbose

    parser = argparse.ArgumentParser(description='CPAP_data_extraction')
    parser.add_argument('source', nargs=1, help='path to CPAP data')
    parser.add_argument('destination', nargs=1, help='path to place extacted \
    data')
    parser.add_argument('-v', action='store_true', help='be verbose')

    args = parser.parse_args()
    source = sys.argv[1]
    destination = sys.argv[2]
    verbose = args.v


def hello_world():
    '''
    Basic hello world, for testing, will be deleted later

    Returns
    --------
    int
        Always 0
    '''
    print("Hello world!")
    return 0


def copy_file(source, destination):
    '''
    Reads a file (source) line by line, and writes each line to another file
    (destination). This function is for testing only, it will be deleted later

    Paramters
    ---------
    source : Path
        The source file to be copied

    destination : Path
        The directory to place the copied file

    Attributes
    ----------
    outfile : string
        The name of the output file, for a file called 'orginal.000', the
        crated file will be called 'original.000_extracted'

    verbose : bool
        if True, print the size of the original and copied file, since this
        function only copies, these two sizes should be the same
    '''
    if not os.path.isfile(source):
        print("ERROR: source file {} not found!".format(source))
        exit()

    if not os.path.isdir(destination):
        print("ERROR: destination directory {} not found!".format(destination))
        exit()

    outfile = '{}/{}_extracted'.format(destination, source)

    with open(source, 'rb') as input:
        with open(outfile, 'wb') as output:
            for line in input:
                output.write(line)

    if verbose:
        print('Done, the original file is size {}, '
              'The extracted file is size {}'
              .format(os.path.getsize(source), os.path.getsize(outfile)))


# Global variables
source = "."
destination = "."
verbose = False

if __name__ == '__main__':
    setup_args()
    copy_file(source, destination)
