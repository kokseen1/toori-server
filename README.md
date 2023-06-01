# Iro 

[![GHCR](https://github.com/kokseen1/toori-server/actions/workflows/ghcr.yml/badge.svg)](https://github.com/kokseen1/toori-server/actions/workflows/ghcr.yml)
[![PyPI Release](https://github.com/kokseen1/toori-server/actions/workflows/release.yml/badge.svg)](https://github.com/kokseen1/toori-server/actions/workflows/release.yml)
[![PyPI Version](https://img.shields.io/pypi/v/toori-server.svg)](https://pypi.python.org/pypi/toori-server/)

Server for a minimal layer 3 tunnel over http(s).

## Deploying with Docker

Instead of installing toori-server on the host, it can be deployed as a Docker container with much convenience.

Pull from GHCR:

```shell
sudo docker pull ghcr.io/kokseen1/toori-server:latest
```

Run the container:

```shell
sudo docker run -d --cap-add=NET_ADMIN -p 80:80 ghcr.io/kokseen1/toori-server
```

#### HTTPS

To deploy with HTTPS, run the container with a bind mount and pass the port and certs directory as arguments:

```shell
sudo docker run -d -v /etc/letsencrypt:/etc/letsencrypt --cap-add=NET_ADMIN -p 443:443 ghcr.io/kokseen1/toori-server 443 /etc/letsencrypt/live/toori.server/
```

## Installation

```shell
pip3 install toori-server --no-binary :all:
```

## Prerequisites

- [Libtins](http://libtins.github.io/download/) (optional, will fallback to Scapy (slow) if not installed)

### RST Packets

Because the Linux kernel sends a `RST` to connections it did not establish, use the following command to ensure that outgoing packets are sent successfully:

```shell
sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -s <local address> -j DROP
```

[See here](https://stackoverflow.com/questions/9058052/unwanted-rst-tcp-packet-with-scapy) for more information.

## Usage

Run with root permissions:

```shell
iro <port>
```

Example with HTTPS:

```shell
iro 443 -c "/etc/letsencrypt/live/toori.server/"
```


