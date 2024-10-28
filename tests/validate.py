#!/usr/bin/env python3

"""
This script reads input from stdin and validates that it is correctly
formatted JSON with expected fields.
"""

import json
import sys

def is_json_formatted(content): # type: (str) -> bool
    """
    Check if given string is JSON formatted

    :param content: String to test format of
    :return: True if string is in JSON format, False otherwise
    """

    try:
        json.loads(content)
        return True
    except ValueError:
        return False

def has_necessary_fields(data): # type: (dict) -> bool
    """
    Check if given dict contains all expected fields.

    :param data: Dict to check
    : return: True if all expected fields are contained, False otherwise
    """

    # Check that expected protocols are contained and not more
    expected_proto_keys = {'tcp4', 'tcp6', 'tcp', 'udp4', 'udp6', 'udp', 'all'}

    # Check that all expected protocols are contained
    for proto_key in expected_proto_keys:
        if proto_key not in data.keys():
            print(f'Error: Data is missing expected key "{proto_key}"!',
                  file=sys.stderr)
            return False

    # Check that no unexpected protocols are contained
    for proto_key in data.keys():
        if proto_key not in expected_proto_keys:
            print(f'Error: Found unexpected key "{proto_key}"!',
                  file=sys.stderr)
            return False

    expected_connection_states = [
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
        'UNKNOWN']

    # Check that all expected connection states are contained
    for proto_key in expected_proto_keys:
        for state in expected_connection_states:
            if state not in data[proto_key]:
                print((f'Error: Protocol "{proto_key}" is missing expected'
                      f' connection state "{state}"!'),
                      file=sys.stderr)
                return False

    # Check that no unexpected connection states are contained
    for proto_key in expected_proto_keys:
        for state in data[proto_key]:
            if state not in expected_connection_states:
                print((f'Error: Found unexpected connection state "{state}"'
                      f' for protocol "{proto_key}"!'),
                      file=sys.stderr)
                return False

    # Check that all connection states have sane values
    for proto_key in expected_proto_keys:
        for state in expected_connection_states:
            val = data[proto_key][state]
            if not isinstance(val, int) or val < 0:
                print((f'Error: State "{state}" for protocol "{proto_key}"'
                      f' has unexpected value "{val}"!'),
                      file=sys.stderr)
                return False

    # Everything is fine
    return True

def main(): # type: () -> int
    """
    Main function
    """

    # Read from stdin
    input_lines = [line.rstrip() for line in sys.stdin]
    input_str = '\n'.join(input_lines)

    # Check if input is json formatted at all
    is_json = is_json_formatted(input_str)
    if not is_json:
        print('Error: Content is not json formatted!', file=sys.stderr)
        print(input_str, file=sys.stderr)
        return 1

    input_dict = json.loads(input_str)
    is_ok = has_necessary_fields(input_dict)
    if not is_ok:
        print('Error: Given data is malformed, data:', file=sys.stderr)
        print(input_str, file=sys.stderr)
        return 1

    # Everything is fine
    return 0

if __name__ == '__main__':
    sys.exit(main())
