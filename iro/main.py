from anyio import wrap_file, run
import time
import os
import struct
from fcntl import ioctl

import socket
from collections import deque
import socketio
from scapy.all import (
    AsyncSniffer,
    get_if_list,
    get_if_addr,
    conf,
    IP,
    TCP,
    UDP,
)
import asyncio
from sanic import Sanic

from engineio.payload import Payload

Payload.max_decode_packets = 2500000

conf.layers.filter([IP, TCP, UDP])

app = Sanic("Iro")
app.config["CORS_SUPPORTS_CREDENTIALS"] = True

sio = socketio.AsyncServer(async_mode="sanic", cors_allowed_origins=[])
sio.attach(app)

packets = deque()

return_nat = dict()
forward_nat = dict()
virtual_ip_map = dict()

NEXT_VIP = 0xC6120000

LINUX_TUNSETIFF = 0x400454CA
LINUX_IFF_TUN = 0x0001
LINUX_IFF_NO_PI = 0x1000
LINUX_IFF_MULTI_QUEUE = 0x0100

TUN_NAME = "tun0"
TUN_IP = "192.0.2.2"

#os.system(f"ip tuntap add name {TUN_NAME} mode tun")
#os.system(f"ip link set {TUN_NAME} up")
#os.system(f"ip addr add 192.0.2.1 peer {TUN_IP} dev {TUN_NAME}")


tun = open("/dev/net/tun", "r+b", buffering=0)
ifs = struct.pack("16sh22s", TUN_NAME.encode(), LINUX_IFF_TUN | LINUX_IFF_NO_PI, b"")
ioctl(tun, LINUX_TUNSETIFF, ifs)


@sio.on("out")
async def handle_outbound(sid, data):
    pkt = IP(data)

    # Virtual LAN
    vtarget = virtual_ip_map.get(pkt.dst)
    if vtarget is not None:
        pkt.src = virtual_ip_map.get((pkt.src, sid))
        pkt.dst, target_sid = vtarget
        await sio.emit("in", bytes(pkt), to=target_sid)
        return

    if pkt.haslayer(TCP) or pkt.haslayer(UDP):

        # Check if existing mapping exists
        # For O(1) lookup for existing connections instead of using the loop below
        fake_sport = forward_nat.get((pkt.sport, sid, pkt.dst, pkt.dport))

        if fake_sport is None:
            decrement = False
            # New first-time connection

            # Try mapping to the real port first
            fake_sport = pkt.sport

            while True:

                # Check if there is an existing connection from proxy:sport -> dst:dport
                rnat_value = return_nat.get((fake_sport, pkt.dst, pkt.dport))

                if rnat_value is not None:
                    # Increment and try the next port

                    if fake_sport == 65535:
                        decrement = True

                    if decrement:
                        fake_sport -= 1
                    else:
                        fake_sport += 1

                    continue

                # Port is available, create entry and break loop

                # proxy:sport -> dst:dport : client:sport, sid
                return_nat[(fake_sport, pkt.dst, pkt.dport)] = (pkt.sport, sid)
                forward_nat[(pkt.sport, sid, pkt.dst, pkt.dport)] = fake_sport
                break

        pkt.sport = fake_sport

    pkt.src = TUN_IP

    # Force recalculaton of layer checksums
    if pkt.haslayer(IP):
        del pkt[IP].chksum
    if pkt.haslayer(TCP):
        del pkt[TCP].chksum
    if pkt.haslayer(UDP):
        del pkt[UDP].chksum

    tun.write(bytes(pkt))



async def assign(sid, local_ip, virtual_ip):
    virtual_ip_map[virtual_ip] = (local_ip, sid)
    virtual_ip_map[(local_ip, sid)] = virtual_ip
    virtual_ip_map[sid] = virtual_ip

    await sio.emit("message", f"Virtual IP: {virtual_ip}", to=sid)


@sio.on("connect")
async def connect(sid, environ, auth):
    print("connect ", sid)
    virtual_ip = auth.get("req_ip")
    local_ip = auth.get("loc_ip")
    if virtual_ip is None or local_ip is None:
        # No vip
        return True

    if virtual_ip.startswith("198.18.0.") and virtual_ip_map.get(virtual_ip) is None:
        await assign(sid, local_ip, virtual_ip)

    else:
        await sio.emit("message", "Requested IP invalid/already in taken", to=sid)
        return False


@sio.on("disconnect")
def disconnect(sid):
    print("disconnect ", sid)

    virtual_ip = virtual_ip_map.get(sid)
    if sid is not None:
        vip_map_value = virtual_ip_map.get(virtual_ip)
        virtual_ip_map.pop(vip_map_value,None)
        virtual_ip_map.pop(virtual_ip,None)
        virtual_ip_map.pop(sid,None)


    for rnat_key, rnat_value in return_nat.copy().items():
        if sid == rnat_value[1]:
            del return_nat[rnat_key]

    for fnat_key in forward_nat.copy().keys():
        if sid == fnat_key[1]:
            del forward_nat[fnat_key]


async def background_sender(app):
    while True:
        await asyncio.sleep(0)

        sid = None

        if len(packets) == 0:
            continue

        pkt = packets.pop()

        if pkt.haslayer(TCP) or pkt.haslayer(UDP):

            rnat_value = return_nat.get((pkt.dport, pkt.src, pkt.sport))

            # Incoming packet without mapping
            if rnat_value is None:
                continue

            pkt.dport, sid = rnat_value

        await sio.emit("in", bytes(pkt), to=sid)

#@app.listener("after_server_start")
async def background_sender(app):
    while True:
        #await asyncio.sleep(0)
        pkt_bytes = await wrap_file(tun).read(2048)
        pkt = IP(pkt_bytes)
        #loop.create_task(sio.emit("in", reply))
    
        sid = None
    
        if pkt.haslayer(TCP) or pkt.haslayer(UDP):
    
            rnat_value = return_nat.get((pkt.dport, pkt.src, pkt.sport))
    
            # Incoming packet without mapping
            if rnat_value is None:
                continue
    
            pkt.dport, sid = rnat_value
    
        #loop.run_until_complete(sio.emit("in", bytes(pkt), to=sid))
        await sio.emit("in", bytes(pkt), to=sid)
 

def start(port, certs_dir=None):
    app.add_task(background_sender)
    app.run(
        "::",
        port=port,
        debug=False,
        access_log=False,
        single_process=True,
        ssl=certs_dir,
    )
   
