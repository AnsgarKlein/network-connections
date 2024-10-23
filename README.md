[![CI](https://github.com/AnsgarKlein/network-connections/actions/workflows/ci.yml/badge.svg)](https://github.com/AnsgarKlein/network-connections/actions/workflows/ci.yml)

network-connections
===================

No dependency Python script that outputs number of open network connections
categorized by state on Linux system.
Useful for integrating in monitoring systems.


Usage
-----

The script does not have any dependencies apart from a Python 3 interpreter.
It should work with very old versions of Python 3.  
Simply copy the script to the system you want to monitor and have your
monitoring system execute it.

Output:

```json
{
    "tcp4": {
        "FIN_WAIT1": 0,
        "ESTABLISHED": 7,
        "TIME_WAIT": 1973,
        "CLOSE": 0,
        "SYN_SENT": 15,
        "SYN_RECV": 0,
        "FIN_WAIT2": 0,
        "LISTEN": 0,
        "CLOSING": 0,
        "CLOSE_WAIT": 0,
        "LAST_ACK": 0,
        "UNKNOWN": 0
    },
    "tcp6": {
        "FIN_WAIT1": 0,
        "ESTABLISHED": 91,
        "TIME_WAIT": 80,
        "CLOSE": 0,
        "SYN_SENT": 0,
        "SYN_RECV": 0,
        "FIN_WAIT2": 0,
        "LISTEN": 0,
        "CLOSING": 0,
        "CLOSE_WAIT": 0,
        "LAST_ACK": 0,
        "UNKNOWN": 0
    },
    "udp4": {
        "FIN_WAIT1": 0,
        "ESTABLISHED": 0,
        "TIME_WAIT": 0,
        "CLOSE": 0,
        "SYN_SENT": 0,
        "SYN_RECV": 0,
        "FIN_WAIT2": 0,
        "LISTEN": 0,
        "CLOSING": 0,
        "CLOSE_WAIT": 0,
        "LAST_ACK": 0,
        "UNKNOWN": 0
    },
    "udp6": {
        "FIN_WAIT1": 0,
        "ESTABLISHED": 0,
        "TIME_WAIT": 0,
        "CLOSE": 0,
        "SYN_SENT": 0,
        "SYN_RECV": 0,
        "FIN_WAIT2": 0,
        "LISTEN": 0,
        "CLOSING": 0,
        "CLOSE_WAIT": 0,
        "LAST_ACK": 0,
        "UNKNOWN": 0
    },
    "tcp": {
        "FIN_WAIT1": 0,
        "ESTABLISHED": 98,
        "TIME_WAIT": 2053,
        "CLOSE": 0,
        "SYN_SENT": 15,
        "SYN_RECV": 0,
        "FIN_WAIT2": 0,
        "LISTEN": 0,
        "CLOSING": 0,
        "CLOSE_WAIT": 0,
        "LAST_ACK": 0,
        "UNKNOWN": 0
    },
    "udp": {
        "FIN_WAIT1": 0,
        "ESTABLISHED": 0,
        "TIME_WAIT": 0,
        "CLOSE": 0,
        "SYN_SENT": 0,
        "SYN_RECV": 0,
        "FIN_WAIT2": 0,
        "LISTEN": 0,
        "CLOSING": 0,
        "CLOSE_WAIT": 0,
        "LAST_ACK": 0,
        "UNKNOWN": 0
    },
    "all": {
        "FIN_WAIT1": 0,
        "ESTABLISHED": 98,
        "TIME_WAIT": 2053,
        "CLOSE": 0,
        "SYN_SENT": 15,
        "SYN_RECV": 0,
        "FIN_WAIT2": 0,
        "LISTEN": 0,
        "CLOSING": 0,
        "CLOSE_WAIT": 0,
        "LAST_ACK": 0,
        "UNKNOWN": 0
    }
}
```
