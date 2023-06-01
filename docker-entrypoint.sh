#!/bin/bash
iptables-legacy -A OUTPUT -p tcp --tcp-flags RST RST -s $(hostname -I) -j DROP
if [ -z "$2" ]
  then
    iro $1
else
    iro $1 -c $2
fi
