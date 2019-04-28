# -*- coding: utf-8 -*-
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

C_Types : dictionary {char: int}
    A dictionary containing the relavent number of bytes for each C Type.
    See https://docs.python.org/3/library/struct.html

verbose : bool
    If True, be verbose
'''
import argparse                 # For command line arguments
import sys                      # Fir command line arguments
import os                       # For file IO
import struct                   # For unpacking binary data
import decorators               # For debugging, see the decorators.py file
import re                       # For cleaning up strings
from datetime import datetime   # For converting UNIX time
import warnings                 # For raising warnings


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


def extract_header_packet(packet):
    '''
    The SpO2 files, stored as .001 files, all have header packets. This method
    extracts the data from those headers, and returns those data

    Parameters
    ----------
    data_file : File
        The .001 file that contains the header to be extracted

    Attributes
    ----------

    verbose : bool
        if True, print 'Now reading the header packet in {source}'

    header : String array
        A String array to be populated with the various fields found in the
        header packet

    fields : Dictionary
        The key of each entry is the name of each of the various fields found
        in the header packet. The value is a tuple, index 0 is the number of
        bytes used by the field, index 1 is the C-type of that field.

        16-bit integers are shorts (h/H), 32-bit integers are ints (i/I),
        64-bit integers are long longs (q/Q). Use the lowercase letter for
        signed integers, and the uppercase format for unsigned integers. '<'
        indicates little Endian, which all the CPAP data appears to be stored
        in

        https://docs.python.org/2/library/struct.html

        magic_number : unsigned 32-bit int
            Determined by machine type, date, etc. not important

        file_version : unsigned 16-bit int
            I have no idea what this is, it doesn't seem to be important

        file_type_data : unisgned 16-bit int
            I have no idea what this is, it doesn't seem to be important

        machine_ID : unsigned 32-bit int
            This machine's ID number

        session_ID : unsigned 32-bit int
            This session's ID number

        start_time : 64-bit int
            The start time of this session, stored in UNIX date-time format

        end_time : 64-bit int
            The end time of this session, stored in UNIX date-time format

        compressed : unsigned 16-bit int
            I have no idea what this is, it doesn't seem to be important

        machine_type : unsigned 16-bit in
            2 indicates pulse oximeter

        data_size : unsigned 32-bit integer
            Indicates the size of the data packets, which follow the header

        crc : unsigned 16-bit integer
            I have no idea what this is, it doesn't seem to be important

        mcsize : unsigned 16-bit integer
            Indicates the number of data streams

    Returns
    -------
    header : String array
        The extracted header data
    '''

    if verbose:
        print('Extracting the header in {}'.format(source))

    fields = {'Magic number': (4, '<I'),
              'File version': (2, '<H'),
              'File type data': (2, '<H'),
              'Machine ID': (4, '<I'),
              'Session ID': (4, '<I'),
              'Start time (UNIX time)': (8, '<q'),
              'End time (UNIX time)': (8, '<q'),
              'Compressed': (2, '<H'),
              'Data size': (4, '<I'),
              'crc': (2, '<H'),
              'mcsize': (4, '<I')}

    header = ['---HEADER---\n']
    for field in fields:
        if verbose:
            print('Unpacking {} in {}'.format(field, source))

        num_of_bytes = fields.get(field)[0]
        read_bytes = packet[:num_of_bytes]
        del packet[:num_of_bytes]
        c_type = fields.get(field)[1]

        header.append('{}: {}\n'.format(field,
                                        struct.unpack(c_type, read_bytes)))

    time = int(re.search(r'\d+', header[6]).group(0))
    header.insert(7, 'Start time: {}\n'.format(convert_unix_time(time)))
    time = int(re.search(r'\d+', header[8]).group(0))
    header.insert(9, 'End time: {}\n'.format(convert_unix_time(time)))

    packet_fields = {'Packet type': (1, '<B'),
                     'u1': (8, 'd'),
                     'u2': (8, 'd'),
                     'Data type': (4, '<I'),
                     'Number of packets': (2, '<H'),
                     'Time 1': (8, 'q'),
                     'Time 2': (8, 'q'),
                     'Pulse change events': (4, '<I'),
                     'Field 2': (1, '<B'),
                     'Double 1': (8, 'd'),
                     'Double 2': (8, 'd')}
                     #'Double 3': (8, 'd'),
                     #'Min value': (8, 'd'),
                     #'Max value': (8, 'd')}
                     
    for field in packet_fields:
        if verbose:
            print('Unpacking {} in {}'.format(field, source))
            print(packet)

        num_of_bytes = packet_fields.get(field)[0]
        read_bytes = packet[:num_of_bytes]
        del packet[:num_of_bytes]
        c_type = packet_fields.get(field)[1]

        header.append('{}: {}\n'.format(field,
                                        struct.unpack(c_type, read_bytes)))

    print(packet)
    return header


def extract_data_packet(packet):
    '''
    The SpO2 files, stored as .001 files, all have data packets which
    immeditaly follow the header packet. This method extracts the data from
    a data packet, and returns those data

    Parameters
    ----------
    packet : bytes
        The data packet, created by read_packet() to be extracted

    Attributes
    ----------

    verbose : bool
        if True, print 'Now reading a data packet in {source}'

    data : String array
        A String array to be populated with the various fields found in the
        data packet

    fields : Dictionary
        The key of each entry is the name of each of the various fields found
        in the data packet. The value is a tuple, index 0 is the number of
        bytes used by the field, index 1 is the C-type of that field.

        16-bit integers are shorts (h/H), 32-bit integers are ints (i/I),
        64-bit integers are long longs (q/Q). Use the lowercase letter for
        signed integers, and the uppercase format for unsigned integers. '<'
        indicates little Endian, which all the CPAP data appears to be stored
        in

        https://docs.python.org/2/library/struct.html

        packet_type : unsigned 8-bit integer
            Indicates what type of packet this is
            TODO: What are the types of packets?


    Returns
    -------
    data : String array
        The extracted data
    '''
    if verbose:
        print('Unpacking data packet from {}'.format(source))

    fields = {'Data type': (2, '<H'),
              'u1': (2, '<H'),
              'Number of packets': (2, '<H'),
              'Start time': (8, '<q'),
              'End time': (8, '<q'),
              'Number of pulse change events': (4, '<I'),
              'Field 2': (1, '<B'),
              'Double 1': (8, 'd'),
              'Double 2': (8, 'd'),
              'Double 3': (8, 'd'),
              'Minimum value': (8, 'd'),
              'Maximum value': (8, 'd'),
              'Final packet type': (1, 'B')}

    data = ['---DATA PACKET---\n']
    for field in fields:
        if verbose:
            print('Unpacking {} in {}'.format(field, source))
            print(packet)

        num_of_bytes = fields.get(field)[0]
        read_bytes = packet[:num_of_bytes]
        del packet[:num_of_bytes]
        c_type = fields.get(field)[1]

        data.append('{}: {}\n'.format(field,
                                      struct.unpack(c_type, read_bytes)))

    print(data[4])
    return data


def extract_Sp02_data(packet):
    '''
    fields : Dictionary
        The key of each entry is the name of each of the various fields found
        in the data packet. The value is a tuple, index 0 is the number of
        bytes used by the field, index 1 is the C-type of that field.

        16-bit integers are shorts (h/H), 32-bit integers are ints (i/I),
        64-bit integers are long longs (q/Q). Use the lowercase letter for
        signed integers, and the uppercase format for unsigned integers. '<'
        indicates little Endian, which all the CPAP data appears to be stored
        in

        https://docs.python.org/2/library/struct.html
    '''

    fields = {'Magic number': (4, '<I'),
              'File version': (2, '<H'),
              'File type data': (2, '<H'),
              'Machine ID': (4, '<I'),
              'Session ID': (4, '<I'),
              'First start time': (8, '<q'),
              'First end time': (8, '<q'),
              'Compression': (2, '<H'),
              'Machine type': (2, '<H'),
              'Data size': (4, '<I'),
              'crc': (2, '<H'),
              'Number of data streams': (2, '<H'),
              'Event size': (2, '<H'),
              'Key1': (2, '<H'),
              'Exist Sp02 sessions': (2, '<H')}

    data = []
    for field in fields:
        if verbose:
            print('Unpacking {} in {}'.format(field, source))
            print(packet)

        num_of_bytes = fields.get(field)[0]
        read_bytes = packet[:num_of_bytes]
        del packet[:num_of_bytes]
        c_type = fields.get(field)[1]

        data.append('{}: {}\n'.format(field,
                                      struct.unpack(c_type, read_bytes)))

    return data


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


def read_packet(data_file, delimeter):
    '''
    Packets are sepearted using a delimeter, the .001 files, for example, use
    \xff\xff\xff\xff as their delimeter. This packet reads and returns all data
    stored in data_file up to delimeter. The data are stored with varrying
    length, some data fields are a single byte, some are 16 bytes. Because of
    this, even if we know the delimeter is four bytes, we cannot read the data
    file four bytes at a time. We must instead read one byte at a time. Once
    each byte is read in, this method checks if that byte is the first part of
    the delimeter. If it isn't, the byte is appended to packet. If it is, this
    method seeks back one byte, then checks if the next bytes match the
    delimeter, if they do, the packet is completely read, so this method
    returns. TODO: Make this explanation less terrible.

    Parameters
    ----------
    data_file : File
        A file object created by read_file(), this object contains the data
        packets to be read

    delimeter : bytes
        The 'separator' of the packets in data_file. For .001 files, the
        delimeter is b'\xff\xff\xff\xff'

    Attributes
    ----------
    packet : bytes
        The complete packet of bytes to be returned

    byte : bytes
        A single byte of data. If this byte isn't part of the delimeter, it
        gets appended to packet
    '''

    packet = b''

    while True:
        byte = data_file.read(1)
        if byte == delimeter[0].to_bytes(1, 'little'):
            data_file.seek(-1, 1)
            if data_file.read(len(delimeter)) == delimeter:
                break
        elif byte == b'':
            break

        packet += byte

    return bytearray(packet)


def extract_packet(packet, fields):
    '''
    Extracts packets into their specified fields

    Parameters
    ----------
    packet : Bytes
        The packet, created by read_packet() to be extracted

    fields : The varying data fields that are expected to be found within
             packet

    Attributes
    ----------

    verbose : bool
        if True, print 'Extracting {field} from {source}

    C_Types : dictionary {character: int}
        The keys of this dictionary indicate a C_Type, and the values indicate
        the corresponding size of that C_Type. For more info, see
        https://docs.python.org/3/library/struct.html 

    data : String array
        A String array to be populated with the various fields found in the
        packet

    field : {string: character}
        Contains the name of the field (e.g., Start time, machine ID, etc.),
        and the C_Type of that field (e.g., H, I, L, etc.)

    number_of_bytes : int
        The number of bytes used by the current field, determined by that
        fields' C_Type

    bytes_to_be_extracted : Bytes array
        The appropriate number of Bytes, taken from packet, to be unpacked

    extracted_line : String
        The fully extracted line, ready to be appeneded to data. 
        Example: Start Time: 1553245673000

    Notes
    --------
    Once the bytes from packet are correctly read and appended to data, they
    are removed from packet. This is simply to make parsing the data cleaner

    All the data are little endian, struct.unpack() expects a '<' before the
    C_Type to specifiy if the Bytes are little endian, which is why a '<' is
    prepended to the C_Type


    Returns
    -------
    data : String array
        The extracted data
    '''

    global C_Types
    data = []

    for field in fields:
        if verbose:
            print('Extracting {} from {}'.format(field, source))
            
        C_Type = fields.get(field)
        number_of_bytes = C_Types.get(C_Type)
        bytes_to_be_extracted = packet[:number_of_bytes]
        del packet[:number_of_bytes]
        C_Type = '<' + C_Type 
        extracted_line = struct.unpack(C_Type, bytes_to_be_extracted)
        data.append('{}: {}\n'.format(field, extracted_line))

    return data


def convert_unix_time(unixtime):
    '''
    Converts an integer, unitime, to a human-readable year-month-day,
    hour-minute-second format. The raw data stores time values in milliseconds
    which is UNIX time * 1000, this method corrects for that.

    Paramters
    ---------
    unixtime : int
        The UNIX time number to be converted

    Returns
    --------
    human-readable-time : string
        The UNIX time converted to year-month-day, hour-minute-second format
    '''

    try:
        unixtime = int(unixtime / 1000)
    except TypeError:
        return 'ERROR: {} is invalid'.format(unixtime)

    if unixtime <= 0:
        warnings.warn('WARNING: UNIX time in {} evaluated to 0')

    if unixtime >= 2147483647:
        warnings.warn('WARNING: UNIX time in {} evaluated to beyond the year \
                       2038, if you really are from the future, hello!')

    return datetime.utcfromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')


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
        If True, print 'Now writing out source.JSON', where 'source' is the
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

    with open(destination + '/' + output_name, 'a') as output:
        for line in File:
            output.write(str(line))


# Global variables
source = "."
destination = "."
verbose = False

# See https://docs.python.org/3/library/struct.html
C_Types = {'c': 1,
           'b': 1,
           'B': 1,
           'h': 2,
           'H': 2,
           'i': 4,
           'I': 4,
           'l': 4,
           'L': 4,
           'q': 8,
           'Q': 8,
           'f': 4,
           'd': 8}


if __name__ == '__main__':
    setup_args()

    data_file = open_file(source)
    packet_delimeter = b'\xff\xff\xff\xff'

    '''
    header_packet = read_packet(data_file, delimeter)
    header = extract_header_packet(header_packet)
    data_packet = read_packet(data_file, delimeter)
    data = extract_data_packet(data_packet)

    write_file(header, destination)
    write_file(data, destination)
    '''

    packets = []
    while True:
        packet = read_packet(data_file, packet_delimeter)
        if packet == b'':
            break
        packets.append(packet)

    fields = {'Magic number': 'I',
              'File version': 'H',
              'File type data': 'H',
              'Machine ID': 'I',
              'Session ID': 'I',
              'First start time': 'q',
              'First end time': 'q'}

    data = extract_packet(packets[0], fields)
    write_file(data, destination)
