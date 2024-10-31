[![CI](https://github.com/AnsgarKlein/network-connections/actions/workflows/ci.yml/badge.svg)](https://github.com/AnsgarKlein/network-connections/actions/workflows/ci.yml)

network-connections
===================

No dependency Python script that outputs number of open network connections
categorized by state on Linux system. Similar to what `netstat` does.
Useful for integrating in monitoring systems.

It does this by reading and parsing virtual files `/proc/net/tcp`,
`/proc/net/tcp6`, `/proc/net/udp`, `/proc/net/udp6` provided by the Linux
kernel.


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

The connection states match `netstat`s ouput:

  - **ESTABLISHED**  
    The socket has an established connection.

  - **SYN_SENT**  
    The socket is actively attempting to establish a connection.

  - **SYN_RECV**  
    A connection request has been received from the network.

  - **FIN_WAIT1**  
    The socket is closed, and the connection is shutting down.

  - **FIN_WAIT2**  
    Connection is closed, and the socket is waiting for a shutdown from the remote end.

  - **TIME_WAIT**  
    The socket is waiting after close to handle packets still in the network.

  - **CLOSE**  
    The socket is not being used.

  - **CLOSE_WAIT**  
    The remote end has shut down, waiting for the socket to close.

  - **LAST_ACK**  
    The remote end has shut down, and the socket is closed. Waiting for acknowledgement.

  - **LISTEN**  
    The socket is listening for incoming connections.

  - **CLOSING**  
    Both sockets are shut down but we still don't have all our data sent.

  - **UNKNOWN**  
    The state of the socket is unknown.
