'''
This module will take raw CPAP data as an input, and export it to JSON as an
output.

Example
-------
    $ python cpap_extraction.py 38611.000 .

Extracts the raw CPAP data from 38611.000 to a new file called 
38611_extracted.JSON

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
    verbose : bool
        if True, print the size of the original and copied file.

    Notes
    -----
    Verbose will only work if the extracted file is put into the same
    directory as the source file, I'm not going to bother fixing this since
    this code will be deleted anyway
    '''

    File = read_file(source)
    write_file(File, destination)

    if verbose:
        try:
            print('Done, the original file is size {}, '
                  'The extracted file is size {}'
                  .format(os.path.getsize(source),
                          os.path.getsize(source.split('.')[0] +
                                          '_extracted.JSON')))
        except FileNotFoundError:
            print('Couldn\'t find the extracted file, did you place it in '
                  'the same directory as the source file?')


def read_file(source):
    '''
    Reads a source from the users' drive and returns the source as File

    Parameters
    ----------
    source : Path
        The file to be read

    Attributes
    ---------
    file : File
        The read-in file, now stored in memory

    verbose : bool
        if True, print 'Now reading in {source}'
    '''

    if verbose:
        print('Now reading in {}'.format(source))

    if not os.path.isfile(source):
        raise FileNotFoundError(
                'ERROR: source file {} not found!'.format(source))

    File = open(source, 'rb')
    return File


def write_file(File, destination):
    '''
    Writes File out to the users' drive, in directory destination

    Parameters
    ----------
    File : file
        The file to be written out

    destination : Path
        The directory to place the written out file

    Attributes
    ----------
    source : String
        The name of the original file

    output_name : String
        The name of the output file

    verbose : bool
        if True, print 'Now writing out source.JSON', where 'source' is the
        name of the orginal file.
    '''

    global source
    # Get everything from the source's filename before the file extention, and
    # append '_extracted.JSON'
    output_name = source.split('.')[0] + '_extracted.JSON'

    if verbose:
        print('Now writting {} to {}'.format(output_name, destination))

    if not os.path.isdir(destination):
        raise FileNotFoundError(
            'ERROR: destination directory {} not found!'.format(destination))

    with open(destination + '/' + output_name, 'w') as output:
        for line in File:
            output.write(str(line))


# Global variables
source = "."
destination = "."
verbose = False

if __name__ == '__main__':
    setup_args()
    copy_file(source, destination)
