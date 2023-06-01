FROM ubuntu:22.04
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3 python3-pip python3-dev libpcap-dev libssl-dev git cmake make build-essential
RUN git clone https://github.com/mfontanini/libtins.git /tmp/libtins
RUN cd /tmp/libtins && git reset --hard b7e61f4c76ac64053c9c4c9f8eadaabbe3a9381a && mkdir build  \
    && cd build  \
    && cmake ../ -DLIBTINS_ENABLE_CXX11=1  \
    && make  \
    && make install
RUN ldconfig
RUN pip3 install toori-server --no-binary :all:
RUN apt-get install -y iptables
COPY ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
