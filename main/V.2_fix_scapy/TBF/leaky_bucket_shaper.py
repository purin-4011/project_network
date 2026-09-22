#!/usr/bin/env python3
"""
leaky_bucket_shaper.py — Part D: Implement Leaky Bucket ด้วย Python
กลุ่ม G19 ได้ algorithm: leaky_bucket จาก generate_group_params.py จึง "ต้องทำ" ส่วนนี้
(ไม่ใช่ optional — เพราะ Linux tc ทำ Token Bucket เท่านั้น จำลอง Leaky Bucket แท้ไม่ได้)

การแปลงหน่วยจาก parameter ประจำกลุ่ม (token_rate_kbit=256, bucket_size_kbit=32,
packet_size_bytes=1400) เป็นหน่วย packet/sec และ packet ที่ LeakyBucket ต้องการ:

    drain_rate_pps  = (token_rate_kbit * 1000 / 8) / packet_size_bytes
                     = (256 * 1000 / 8) / 1400  ≈ 22.86  -> ปัดเป็น 23 pps
    bucket_capacity = (bucket_size_kbit * 1000 / 8) / packet_size_bytes
                     = (32 * 1000 / 8) / 1400   ≈ 2.86   -> ปัดเป็น 3 packets

หมายเหตุ: bucket_capacity ของกลุ่มนี้เล็กมาก (3 packets) เพราะ bucket_size_kbit
ที่สุ่มได้มีค่าน้อย ผลคือ buffer จะเต็มไวและ drop เยอะเมื่อเจอ burst — เป็นพฤติกรรม
ที่คาดหวังของ Leaky Bucket ที่ capacity เล็ก ควรอธิบายจุดนี้ในรายงาน Part F
"""
import time
import threading
import queue


class LeakyBucket:
    def __init__(self, drain_rate_pps, bucket_capacity):
        """
        drain_rate_pps: อัตราการปล่อย packet ออก (packet/sec)
        bucket_capacity: ขนาด buffer สูงสุด (packet)
        """
        self.drain_rate = drain_rate_pps
        self.capacity = bucket_capacity
        self.buffer = queue.Queue(maxsize=bucket_capacity)
        self.dropped = 0
        self.sent = 0
        self._running = True

    def add_packet(self, packet):
        try:
            self.buffer.put_nowait(packet)
        except queue.Full:
            self.dropped += 1
            print(f'[DROP] Buffer เต็ม, packet ถูกทิ้ง (total dropped: {self.dropped})')

    def start_draining(self, output_callback):
        interval = 1.0 / self.drain_rate

        def drain_loop():
            while self._running:
                try:
                    packet = self.buffer.get(timeout=interval)
                    output_callback(packet)
                    self.sent += 1
                except queue.Empty:
                    pass
                time.sleep(interval)

        threading.Thread(target=drain_loop, daemon=True).start()

    def stop(self):
        self._running = False


if __name__ == '__main__':
    def output(pkt):
        print(f'[SEND @ {time.time():.3f}] {pkt}')

    # กลุ่ม G19: แปลงจาก token_rate_kbit=256, bucket_size_kbit=32, packet_size_bytes=1400
    DRAIN_RATE_PPS = 23
    BUCKET_CAPACITY = 3

    bucket = LeakyBucket(drain_rate_pps=DRAIN_RATE_PPS, bucket_capacity=BUCKET_CAPACITY)
    bucket.start_draining(output)

    # จำลอง bursty input
    for i in range(50):
        bucket.add_packet(f'packet-{i}')
        time.sleep(0.01)  # burst เร็วกว่า drain rate มาก

    time.sleep(5)
    bucket.stop()
    print(f'\nสรุป: ส่งสำเร็จ {bucket.sent}, ถูกทิ้ง {bucket.dropped}')
