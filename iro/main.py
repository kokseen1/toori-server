from collections import deque
import socketio
from scapy.all import (
    AsyncSniffer,
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

LOCAL_IP = get_if_addr(conf.iface)

app = Sanic("Iro")
app.config["CORS_SUPPORTS_CREDENTIALS"] = True

sio = socketio.AsyncServer(async_mode="sanic", cors_allowed_origins=[])
sio.attach(app)

packets = deque()

try:
    import _iro

    def inj_fn(ip_layer):

        _iro.inj(bytes(ip_layer))

except ModuleNotFoundError:
    print(f"Iro was not installed with Libtins. Using Scapy for sending.")

    scapy_l3_socket = conf.L3socket()

    def inj_fn(ip_layer):

        # Force recalculaton of layer checksums
        if ip_layer.haslayer(IP):
            del ip_layer[IP].chksum
        if ip_layer.haslayer(TCP):
            del ip_layer[TCP].chksum
        if ip_layer.haslayer(UDP):
            del ip_layer[UDP].chksum

        scapy_l3_socket.send(ip_layer)


@sio.on("out")
async def handle_outbound(sid, data):
    ip_layer = IP(data)
    ip_layer.src = LOCAL_IP

    inj_fn(ip_layer)


@sio.on("connect")
def connect(sid, environ):
    print("connect ", sid)


@sio.on("disconnect")
def disconnect(sid):
    print("disconnect ", sid)


def handle_inbound_packet(pkt):
    packets.appendleft(pkt[IP])


async def background_sender(app):
    while True:
        if len(packets) > 0:
            await sio.emit("in", bytes(packets.pop()))
        await asyncio.sleep(0)


def start(port, certs_dir=None):

    AsyncSniffer(
        filter=f"src host not {LOCAL_IP} and ip and dst port not {port} and dst port not 22",
        store=False,
        prn=lambda pkt: handle_inbound_packet(pkt),
    ).start()

    app.add_task(background_sender)
    app.run(
        "::",
        port=port,
        debug=False,
        access_log=False,
        single_process=True,
        ssl=certs_dir,
    )
