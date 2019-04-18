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
import struct               # For unpacking binary data
import binascii             # For unpacking binary data
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

    File = open_file(source)
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


def open_file(source):
    '''
    Reads a source from the users' drive and returns the source as File

    Parameters
    ----------
    source : Path
        The file to be read

    Attributes
    ----------
    file : File
        The read-in file, now stored in memory

    verbose : bool
        if True, print 'Reading in {source}'

    Returns
    -------
    File : The read-in file
    '''

    if verbose:
        print('Reading in {}'.format(source))

    if not os.path.isfile(source):
        raise FileNotFoundError(
                'ERROR: source file {} not found!'.format(source))

    File = open(source, 'rb')
    return File


def extract_header(data_file):
    '''
    The SpO2 files, stored as .001 files, all have header packets. This method
    extracts the data from those headers, and returns those data

    Parameters
    ----------
    data_file : File
        The .001 file that contains the header to be read

    Attributes
    ----------

    verbose : bool
        if True, print 'Now reading the header packet in {source}'

    header : String array
        A String array to be populated with the following fields, all of which
        are part of the header packet

        magic_number : unsigned 32-bit int
            TODO: What?

        file_version : unsigned 16-bit int
            TODO: What?

        file_type_data : unisgned 16-bit int
            TODO: What?

        machine_ID : unsigned 32-bit int
            This machine's ID number

        session_ID : unsigned 32-bit int
            This session's ID number

        start_time : 64-bit int
            The start time of this session, stored in UNIX date-time format

        end_time : 64-bit int
            The end time of this session, stored in UNIX date-time format

        compressed : unsigned 16-bit int
            TODO: What?

        machine_type : unsigned 16-bit in
            2 indicates pulse oximeter
            TODO: What are the other types?

        data_size : unsigned 32-bit integer
            Indicates the size of the data packets, which follow the header

        crc : unsigned 16-bit integer
            TODO: What?

        mcsize : unsigned 16-bit integer
            Indicates the number of data streams
            TODO: What?

    Returns
    -------
    header : String array
        The extracted header data
    '''

    if verbose:
        print('Extracting the header in {}'.format(source))

    # https://docs.python.org/2/library/struct.html
    # We need to convert to C-types. This means the 16-bit integers are
    # shorts (h/H), the 32-bit integers are ints (i/I), and the 64-bit
    # integers are longs (l/L). Use the lowercase format for signed
    # integers, and the uppercase format for unsigned integers. '<'
    # indicates little Endian
    fields = {'Magic number' : (4, '<I'),
              'File version' : (2, '<H'),
              'File type data' : (2, '<H'),
              'Machine ID' : (4, '<I'),
              'Session ID' : (4, '<I'),
              'Start time' : (8, '<l'),
              'End time' : (8, '<l'),
              'Compressed' : (2, '<H'),
              'Data size' : (4, '<I'),
              'crc' : (2, '<H'),
              'mcsize' : (4, '<I')}

    header = []
    for field in fields:
        if verbose:
            print('Unpacking {}'.format(field))

        print(num_of_bytes)
        read_bytes = data_file.read(num_of_bytes)
        c_type = fields.get(field)[1]

        header.append('{}: {}'.format(field, struct.unpack(c_type, read_bytes)))

    '''
    magic_number = data_file.read(4)
    magic_number = struct.unpack('<I', magic_number)
    file_version = data_file.read(2)
    file_version = struct.unpack('<H', file_version)
    file_type_data = struct.unpack('<H', data_file.read(2))

    header = []
    header.append('File name: {}'.format(source))
    header.append('Magic number: {}'.format(magic_number))
    header.append('File version: {}'.format(file_version))
    header.append('File type data: {}'.format(file_type_data))
    '''

    print(header)


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
    data_file = open_file(source)
    extract_header(data_file)
