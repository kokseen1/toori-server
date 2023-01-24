#include <string>

#include <tins/tins.h>

#include <pybind11/pybind11.h>

namespace py = pybind11;

using namespace Tins;

PacketSender sender;

void inj(std::string pkt)
{
    py::gil_scoped_release release;

    IP ip = IP((uint8_t *)pkt.data(), pkt.size());

    try
    {
        sender.send(ip);
    }
    catch (const std::runtime_error &error)
    {
    }
}

PYBIND11_MODULE(_iro, m)
{
    m.def("inj", &inj);
}