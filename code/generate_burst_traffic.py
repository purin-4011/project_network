#!/usr/bin/env python3
"""
generate_burst_traffic.py — Part C: สร้าง Bursty Traffic ด้วย Scapy

กลุ่ม G19 — burst_size_packets=97, packet_size_bytes=1400, burst_interval_ms=500
(จาก generate_group_params.py G19)

fix scapy to use 1 socket to sent all packet so that packet will send faster than token generate
"""
from scapy.all import IP, UDP, Raw, conf
import time
import sys
import errno


def send_burst(dst_ip, burst_size, packet_size, interval_ms, num_bursts=10):
    payload = 'X' * packet_size
    s = conf.L3socket(iface="h1-eth0")   # เปิดครั้งเดียว ก่อนเข้า loop ทั้งหมด
    dropped = 0

    for burst_num in range(num_bursts):
        print(f'Burst {burst_num + 1}: ส่ง {burst_size} packets')
        for _ in range(burst_size):
            pkt = IP(dst=dst_ip) / UDP(dport=5000) / Raw(load=payload)
            try:
                s.send(pkt)
            except OSError as e:
                if e.errno == errno.ENOBUFS:
                    dropped += 1
                else:
                    raise
        time.sleep(interval_ms / 1000)

    s.close()   # ปิดครั้งเดียว หลังจบครบทุก burst
    print(f'ทิ้งไปทั้งหมด (ENOBUFS): {dropped} packets')


if __name__ == '__main__':
    DST_IP = "10.0.0.2"

    BURST_SIZE = 97      # burst_size_packets ของกลุ่ม G19
    PACKET_SIZE = 1400   # packet_size_bytes ของกลุ่ม G19
    INTERVAL_MS = 500    # burst_interval_ms ของกลุ่ม G19

    send_burst(DST_IP, BURST_SIZE, PACKET_SIZE, INTERVAL_MS)
