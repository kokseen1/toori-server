# Iro 

[![GHCR](https://github.com/kokseen1/toori-server/actions/workflows/ghcr.yml/badge.svg)](https://github.com/kokseen1/toori-server/actions/workflows/ghcr.yml)
[![PyPI Release](https://github.com/kokseen1/toori-server/actions/workflows/release.yml/badge.svg)](https://github.com/kokseen1/toori-server/actions/workflows/release.yml)
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

## Deploying with Docker

Instead of installing toori-server on the host, it can alternatively be deployed as a Docker container.

Pull from GHCR:

```shell
sudo docker pull ghcr.io/kokseen1/toori-server:latest
```

Run the container:

```shell
sudo docker run -d --cap-add=NET_ADMIN -p 80:80 ghcr.io/kokseen1/toori-server
```

#### HTTPS

To deploy with HTTPS, modify `docker-entrypoint.sh` to point to the certs directory:

```shell
iro 443 -c /path/to/certs/
# iro 80
```

Run the container:

```shell
docker run -d -v /etc/letsencrypt:/path/to/certs --cap-add=NET_ADMIN -p 443:443 ghcr.io/kokseen1/toori-server
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


