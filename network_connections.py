#!/usr/bin/env python3

import sys
import subprocess
import os
import json

from typing import Dict
from typing import List

def run_netstat() -> str:
    netstat_cmd = [
        'netstat',
        '--numeric',
        '--wide',
        '--protocol=inet,inet6'
    ]

    try:
        environ = os.environ.copy()
        environ['LC_ALL'] = 'en_US'

        cmd = subprocess.run(
            netstat_cmd,
            env=environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True)

        if cmd.returncode != 0:
            raise Exception(f'Error running netstat: {cmd.stderr}')

        return cmd.stdout
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        raise e

def tokenize_netstat_headers(headers_line: str, all_lines: List[str]) -> List[str]:
    def is_whitespace_column(index: int) -> bool:
        for line in all_lines:
            # Index is not on this line
            if len(line) < index:
                return False

            if line[index] not in [' ', '\\t']:
                return False


        return True

    headers = []
    current_header = ''
    for i, c in enumerate(headers_line):
        if c not in [' ', '\\t']:
            current_header += c
        else:
            # Check if whitespace may be end of header string
            if is_whitespace_column(i):
                # If we finished a header string add it to list of headers
                if current_header != '':
                    headers.append(current_header)
                current_header = ''
            else:
                current_header += c
    # Add last header
    if current_header != '':
        headers.append(current_header)

    #If this is the second space we found in a row it is highly
    #unlikely that we are still parsing the same header.
    #if len(current_header) > 1 and current_header[-1] == ' ' or current_header[-1] == '\\t':

    # Strip whitespaces from headers
    headers = [h.strip() for h in headers]

    return headers

def tokenize_netstat_data(data_lines: List[str], headers: List[str]) -> List[Dict]:
    data_list = []

    for line in data_lines:
        columns = line.split(' ')
        columns = [c for c in columns if c != '']

        if len(columns) != len(headers):
            raise Exception((f'Parsed more or less columns than expected in line: {line}.',
                             f'Expected the values for the following: {", ".join(headers)}'))

        # Create data entry with correct header names in correct order
        data_entry = {header: columns[i] for i, header in enumerate(headers)}
        data_list.append(data_entry)

    return data_list

def parse_netstat_output(stdout: str):
    all_lines = stdout.strip().split('\n')
    all_lines = [l.strip() for l in all_lines]

    if len(all_lines) < 2:
        raise Exception('Cannot parse netstat output, output does not contain enough lines')

    # Ignore first line, it contains useless info
    # Headers are in the second line, the rest is data
    headers_line = all_lines[1]
    data_lines = all_lines[2:]

    # Get list of headers from header line
    headers = tokenize_netstat_headers(headers_line, [headers_line] + data_lines)

    # Parse data lines into list of dicts with help of header list
    data_list = tokenize_netstat_data(data_lines, headers)
    return data_list

def post_process_data(data_list: List[Dict]) -> List[Dict]:
    # Data entries are guaranteed to all have the same keys, so we
    # just need to check in one of them.
    if 'Proto' not in data_list[0]:
        raise Exception('Could not find column "Proto" in netstat output')

    output = []
    for entry in data_list:
        copy = dict(entry)

        if copy['Proto'] == 'tcp':
            copy['Proto'] = 'tcp4'
        elif copy['Proto'] == 'udp':
            copy['Proto'] = 'udp4'

        output.append(copy)

    return output

def count_connections(data_list: List[Dict]) -> Dict:
    # Data entries are guaranteed to all have the same keys, so we
    # just need to check in one of them.
    if 'State' not in data_list[0]:
        raise Exception('Could not find column "State" in netstat output')
    if 'Proto' not in data_list[0]:
        raise Exception('Could not find column "Proto" in netstat output')

    supported_states = [
        'ESTABLISHED',
        'SYN_SENT',
        'SYN_RECV',
        'FIN_WAIT1',
        'FIN_WAIT2',
        'TIME_WAIT',
        'CLOSE',
        'CLOSE_WAIT',
        'LAST_ACK',
        'LISTEN',
        'CLOSING',
        'UNKNOWN',
    ]
    supported_protocols = ['tcp', 'udp', 'tcp4', 'tcp6', 'udp4', 'udp6']

    # Create empty dict for counting
    #   connections = {
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
    connections: dict = {proto: {} for proto in supported_protocols}
    for proto in supported_protocols:
        for state in supported_states:
            connections[proto][state] = 0

    # Go through all entries and count number of states/protocols
    for entry in data_list:
        proto = entry['Proto']
        state = entry['State']

        # Skip unknown protocols or connection states
        if entry['Proto'] not in supported_protocols:
            print(f'Unsupported protocol: {entry["Proto"]}', file=sys.stderr)
            continue
        if entry['State'] not in supported_states:
            print(f'Unsupported connection state: {entry["State"]}', file=sys.stderr)
            continue

        # Count connection
        connections[proto][state] += 1

    # Add v4 and v6 protocols and sum up all protocols
    connections['all'] = {}
    for state in supported_states:
        connections['tcp'][state] = connections['tcp4'][state] + connections['tcp6'][state]
        connections['udp'][state] = connections['udp4'][state] + connections['udp6'][state]

        connections['all'][state] = connections['tcp'][state] + connections['udp'][state]

    return connections

def main() -> None:
    # Run netstat and capture stdout
    netstat_stdout = run_netstat()

    # Parse output of netstat
    data_list = parse_netstat_output(netstat_stdout)
    data_list = post_process_data(data_list)

    # Count connections in different states for different protocols
    connections = count_connections(data_list)

    # Output as json
    print(json.dumps(connections, indent=4))

if __name__ == '__main__':
    main()
