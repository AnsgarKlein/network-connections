#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2024 Ansgar Klein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""
This script reads connection info from virtual kernel files /proc/net/tcp,
/proc/net/tcp6, /proc/net/udp, /proc/net/udp6 similar to the netstat command.

This information is parsed and categorized by connection protocol and
connection state. It is then printed out in JSON format.
"""

import argparse
import json
import os
import re
import sys


# Map from state enum number to string
# Taken from Linux kernel source at /include/net/tcp_states.h
STATE_MAP = {
    1: 'ESTABLISHED',
    2: 'SYN_SENT',
    3: 'SYN_RECV',
    4: 'FIN_WAIT1',
    5: 'FIN_WAIT2',
    6: 'TIME_WAIT',
    7: 'CLOSE',
    8: 'CLOSE_WAIT',
    9: 'LAST_ACK',
    10: 'LISTEN',
    11: 'CLOSING',
    12: 'UNKNOWN',  # Actually TCP_NEW_SYN_RECV
    13: 'UNKNOWN',  # Actually BOUND_INACTIVE
}


def get_raw_connection_data(proc='/proc'): # type: (str) -> tuple
    """
    Read kernel files and return tuple of contents.

    Read virtual files /proc/net/tcp, /proc/net/tcp6, /proc/net/udp,
    /proc/net/udp6 remove the first line (contains header) and split them on
    newline character.
    Return tuple of list of line strings.
    Every file is returned in a separate list.

    :param proc: Path to /proc. Usually only needed for testing purposes.
    :raises Exception: When /proc path given does not exist
    :return: 4-Tuple of list of lines of four files
    """

    if not os.path.exists(proc):
        raise Exception(f'Path "{proc}" does not exist!')

    def get_lines_of_file(path): # type: (str) -> list
        with open(path, encoding='ascii') as f:
            content = f.read()
            lines = content.split('\n')
            lines = [l.strip() for l in lines]
            lines = [l for l in lines if l != '']
            return lines

    tcp4 = get_lines_of_file(os.path.join(proc, 'net/tcp'))
    tcp6 = get_lines_of_file(os.path.join(proc, 'net/tcp6'))
    udp4 = get_lines_of_file(os.path.join(proc, 'net/udp'))
    udp6 = get_lines_of_file(os.path.join(proc, 'net/udp6'))

    # Skip headers
    tcp4 = tcp4[1:]
    tcp6 = tcp6[1:]
    udp4 = udp4[1:]
    udp6 = udp6[1:]

    return tcp4, tcp6, udp4, udp6

def parse_raw_connection_data(tcp4, tcp6, udp4, udp6): # type: (list, list, list, list) -> list
    """
    Parse given list of TCP 4/6, UDP 4/6 lines and return result as list of dicts.

    :param tcp4: List of tcp4 lines
    :param tcp6: List of tcp6 lines
    :param udp4: List of udp4 lines
    :param udp6: List of udp6 lines
    :return: List of dictionaries containing info from all given strings
    """

    # Regular expression pattern for extracting fields from string
    tcp_pattern_str = [
        r'^',
        r'([0-9]+):',                          # "sl" column
        r'\s+',
        r'([0-9A-Fa-f]{32}|[0-9A-Fa-f]{8})',   # "local_address" column (ip only)
        r':',                                  # "local_address" column delimiter
        r'([0-9A-Fa-f]{32}|[0-9A-Fa-f]{4})',   # "local_address" column (port only)
        r'\s+',
        r'([0-9A-Fa-f]{32}|[0-9A-Fa-f]{8})',   # "rem_address" column (ip only)
        r':',                                  # "rem_address" column delimiter
        r'([0-9A-Fa-f]{32}|[0-9A-Fa-f]{4})',   # "rem_address" column (port only)
        r'\s+',
        r'([0-9A-Fa-f]{2})',                   # "st" column
        r'\s+',
        r'([0-9A-Fa-f]+)',                     # "tx_queue" column
        r':',
        r'([0-9A-Fa-f]+)',                     # "rx_queue" column
        r'\s+',
        r'([0-9A-Fa-f]+)',                     # "tr" column
        r':',
        r'([0-9A-Fa-f]+)',                     # "tm->when" column
        r'\s+',
        r'([0-9A-Fa-f]+)',                     # "retrnsmt" column
        r'\s+',
        r'([0-9]+)',                           # "uid" column
        r'\s+',
        r'([0-9]+)',                           # "timeout" column
        r'\s+',
        r'([0-9]+)',                           # "inode" column
        r'\s+',
        r'(.*)$',                              # ??
    ]

    tcp_pattern = re.compile(''.join(tcp_pattern_str))

    def parse_line(line): # type: (str) -> dict
        # Match regular expression
        match = re.match(tcp_pattern, line)

        # Error if line did not match
        if match is None:
            raise Exception(('Could not extract info from line:\n'
                             f'{line}'))

        # Extract fields
        entry = {}
        entry['sl']            = match.groups()[0]
        entry['local_address'] = match.groups()[1]
        entry['local_port']    = match.groups()[2]
        entry['rem_address']   = match.groups()[3]
        entry['rem_port']      = match.groups()[4]
        entry['st']            = match.groups()[5]
        entry['tx_queue']      = match.groups()[6]
        entry['rx_queue']      = match.groups()[7]
        entry['tr']            = match.groups()[8]
        entry['tm->when']      = match.groups()[9]
        entry['retrnsmt']      = match.groups()[10]
        entry['uid']           = match.groups()[11]
        entry['timeout']       = match.groups()[12]
        entry['inode']         = match.groups()[13]

        return entry

    # Parse all TCP 4/6 and UDP 4/6 lines and add protocol info
    connections = []
    for line in tcp4:
        entry = parse_line(line)
        entry['proto'] = 'tcp4'
        connections.append(entry)
    for line in tcp6:
        entry = parse_line(line)
        entry['proto'] = 'tcp6'
        connections.append(entry)
    for line in udp4:
        entry = parse_line(line)
        entry['proto'] = 'udp4'
        connections.append(entry)
    for line in udp6:
        entry = parse_line(line)
        entry['proto'] = 'udp6'
        connections.append(entry)

    return connections

def post_process_connection_data(connections): # type: (list) -> list
    """
    Post-process already parsed connection information.

    Change hex encoded IPv4 and IPv6 addresses to normal
    quad octets / hexadecimal colon-separated format.
    Change hex encoded local and remote port to decimal.
    Remove entries with 0.0.0.0 / 0000:0000:0000:0000:0000:0000:0000:0000
    set as remote address.
    Convert connection state from hex identifier to string value.
    (Copies data. Does not modify input.)

    :param connections: List of dictionaries describing connections
    :return: Post-processed copy of input list
    """

    output = []

    def hex_ip_to_decimal(text):
        output = ''
        if len(text) == 8:
            # IPv4 address
            # pylint: disable=consider-using-f-string
            output = '{}.{}.{}.{}'.format(
                int(text[6:8], 16),
                int(text[4:6], 16),
                int(text[2:4], 16),
                int(text[0:2], 16))
            return output
        if len(text) == 32:
            # IPv6 address
            # pylint: disable=consider-using-f-string
            output = '{}{}:{}{}:{}{}:{}{}:{}{}:{}{}:{}{}:{}{}'.format(
                # Word 1
                text[6:8],
                text[4:6],
                text[2:4],
                text[0:2],

                # Word 2
                text[14:16],
                text[12:14],
                text[10:12],
                text[8:10],

                # Word 3
                text[22:24],
                text[20:22],
                text[18:20],
                text[16:18],

                # Word 4
                text[30:32],
                text[28:30],
                text[26:28],
                text[24:26])
            return output.lower()

        raise Exception(f'Given value "{text}" does not look like an IP address!')

    # Process every entry separately
    for e in connections:
        entry = dict(e)

        # Convert IP addresses and ports of every entry to decimal
        entry['local_address'] = hex_ip_to_decimal(entry['local_address'])
        entry['local_port'] = int(entry['local_port'], 16)
        entry['rem_address'] = hex_ip_to_decimal(entry['rem_address'])
        entry['rem_port'] = int(entry['rem_port'], 16)

        # Drop entries with 0.0.0.0 as remote address
        # netstat also does not show these entries
        if entry['proto'] == 'tcp4' or entry['proto'] == 'udp4':
            if entry['rem_address'] == '0.0.0.0':
                # Skip
                continue
        if entry['proto'] == 'tcp6' or entry['proto'] == 'udp6':
            if entry['rem_address'] == '0000:0000:0000:0000:0000:0000:0000:0000':
                # Skip
                continue

        # Convert state from hex integer to string
        state = 'UNKNOWN'
        state_id = int(entry['st'], 16)
        if state_id < len(STATE_MAP):
            state = STATE_MAP[state_id]
        entry['st'] = state


        output.append(entry)

    return output

def count_connections(connections): # type: (list) -> dict
    """
    Count connections in given list of dictionaries by connection protocol
    and connection state.

    :param connections: List of dictionaries containing info about connections
    :raises Exception: If protocol value or state value could not be found
        in dictionaries
    :return: Dictionary containing number of connections in given state
        categorized by connection protocol.
    """

    # Data entries are guaranteed to all have the same keys, so we
    # just need to check in one of them.
    if len(connections) > 0:
        if 'st' not in connections[0]:
            raise Exception('Could not find state entry "st" in connection entry')
        if 'proto' not in connections[0]:
            raise Exception('Could not find protocol entry "proto" in connection entry')

    supported_states = set(STATE_MAP.values())
    supported_protocols = {'tcp4', 'tcp6', 'udp4', 'udp6'}

    # Create empty dict for counting
    #   statistics = {
    #     'tcp4': {
    #       'ESTABLISHED': 0,
    #       'LISTEN': 0,
    #       ...
    #     },
    #     'tcp6': {
    #       'ESTABLISHED': 0,
    #       'LISTEN': 0,
    #       ...
    #     },
    #     ...
    #   }
    statistics = {proto: {} for proto in supported_protocols} # type: dict
    for proto in supported_protocols:
        for state in supported_states:
            statistics[proto][state] = 0

    # Go through all entries and count number of states/protocols
    for entry in connections:
        proto = entry['proto']
        state = entry['st']

        # Skip unknown protocols or connection states
        if entry['proto'] not in supported_protocols:
            print(f'Unsupported protocol: {entry["proto"]}', file=sys.stderr)
            continue
        if entry['st'] not in supported_states:
            print(f'Unsupported connection state: {entry["st"]}', file=sys.stderr)
            continue

        # Count connection
        statistics[proto][state] += 1

    # Add v4 and v6 protocols and sum up all protocols
    statistics['tcp'] = {}
    statistics['udp'] = {}
    statistics['all'] = {}
    for state in supported_states:
        statistics['tcp'][state] = statistics['tcp4'][state] + statistics['tcp6'][state]
        statistics['udp'][state] = statistics['udp4'][state] + statistics['udp6'][state]

        statistics['all'][state] = statistics['tcp'][state] + statistics['udp'][state]

    return statistics

def main(): # type: () -> None
    """
    Main function
    """

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path',
        type=str,
        metavar='PATH',
        nargs='?',
        default='/proc',
        help='''
            Path of /proc directory.
            This is usually /proc. Other directories are only helpful for
            testing purposes.''')
    args = parser.parse_args()

    proc_path = args.path
    if not os.path.exists(proc_path):
        print(f'Error: Given /proc path "{proc_path}" does not exist!', file=sys.stderr)
        sys.exit(1)

    # Read raw connection info
    tcp4, tcp6, udp4, udp6 = get_raw_connection_data(proc_path)

    # Parse connection info and post-process it
    connections = parse_raw_connection_data(tcp4, tcp6, udp4, udp6)
    connections = post_process_connection_data(connections)

    # Count connections in different states for different protocols
    statistics = count_connections(connections)

    # Output as json
    print(json.dumps(statistics, indent=4))

if __name__ == '__main__':
    main()
