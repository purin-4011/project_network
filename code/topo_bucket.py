#!/usr/bin/env python3
"""
topo_bucket.py — Part A: สร้าง Topology บน Mininet
Topology: h1 -- s1 -- h2

กลุ่ม G19 — ค่า bandwidth_mbps = 2 (จาก generate_group_params.py G19)
"""
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel


def build_topology(bandwidth_mbps):
    net = Mininet(switch=OVSSwitch, link=TCLink)

    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    s1 = net.addSwitch('s1', failMode='standalone')

    # จำกัด bandwidth ที่ link ตามค่าประจำกลุ่ม
    net.addLink(h1, s1, bw=bandwidth_mbps)
    net.addLink(h2, s1, bw=bandwidth_mbps)

    net.start()
    return net


if __name__ == '__main__':
    setLogLevel('info')

    BANDWIDTH = 2  # bandwidth_mbps ของกลุ่ม G19 (จาก generate_group_params.py G19)

    net = build_topology(BANDWIDTH)
    CLI(net)
    net.stop()
