#!/bin/bash
iptables-legacy -A OUTPUT -p tcp --tcp-flags RST RST -s $(hostname -I) -j DROP
iro 80
