# Iro 

[![PyPI Release](https://github.com/kokseen1/Iro/actions/workflows/release.yml/badge.svg)](https://github.com/kokseen1/Iro/actions/workflows/release.yml)
[![PyPI Version](https://img.shields.io/pypi/v/toori-server.svg)](https://pypi.python.org/pypi/toori-server/)

Server for a minimal layer 3 tunnel over http(s).

## Prerequisites

- [Libtins](http://libtins.github.io/download/) (optional, will fallback to Scapy (slow) if not installed)

### RST Packets

Because the Linux kernel sends a `RST` to connections it did not establish, use the following command to ensure that outgoing packets are sent successfully:

```shell
sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -s <local address> -j DROP
```

[See here](https://stackoverflow.com/questions/9058052/unwanted-rst-tcp-packet-with-scapy) for more information.

## Installation

```shell
pip3 install toori-server --no-binary :all:
```

## Usage

Run with root permissions:

```shell
iro <port>
```

Example with HTTPS:

```shell
iro 443 -c "/etc/letsencrypt/live/toori.server/"
```
