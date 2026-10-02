# Lab 14 — คำสั่งอ้างอิง (Traffic Shaping: Token Bucket / Leaky Bucket)

## 0) ติดตั้งเครื่องมือ
```
sudo apt update
sudo apt install -y mininet python3-scapy tcpdump wireshark iproute2
```

## 1) ค่า Parameter ของกลุ่ม G19
```
$ python3 generate_group_params.py G19
=== Parameter สำหรับกลุ่ม G19 ===
  bandwidth_mbps: 2
  token_rate_kbit: 256
  bucket_size_kbit: 32
  burst_size_packets: 97
  burst_interval_ms: 500
  packet_size_bytes: 1400
  algorithm: leaky_bucket   <-- ต้องทำ Part D ด้วย (ไม่ใช่ optional สำหรับกลุ่มนี้)
  latency_ms: 400
```
ค่าทั้งหมดถูกแทนไว้ในไฟล์ทุกไฟล์แล้ว (`topo_bucket.py`, `generate_burst_traffic.py`,
`leaky_bucket_shaper.py`) — ไม่ต้องแก้อะไรเพิ่ม เว้นแต่รหัสกลุ่มเปลี่ยน

## 2) รัน Topology (Part A)
```
sudo python3 topo_bucket.py
mininet> h1 ping -c3 h2
mininet> xterm h1 h2
```

## 3) ตั้งค่า TBF บน h1 (Part B)
ภายใน xterm ของ h1:
```
h1# tc qdisc add dev h1-eth0 root tbf \
    rate 256kbit \
    burst 32kbit \
    latency 400ms

# ตรวจสอบค่าที่ตั้ง
h1# tc -s qdisc show dev h1-eth0
```

> **กลุ่ม G19 ได้ algorithm: leaky_bucket** — คำสั่ง `tc tbf` ข้างบนนี้ใช้ตั้งค่าเพื่อ
> เก็บ before/after pcap ตาม Part B/C ตามปกติ แต่**ผลเปรียบเทียบหลักของกลุ่มนี้ต้องมาจาก
> `leaky_bucket_shaper.py` (Part D)** เพราะ Linux tc ทำได้แค่ Token Bucket จริงๆ
> ไม่ใช่ Leaky Bucket แท้ (ดู "ข้อจำกัดของการจำลองด้วย tc" ในเอกสาร §14.6)

ลบ qdisc เพื่อ reset ก่อนทดลองรอบใหม่:
```
h1# tc qdisc del dev h1-eth0 root
```

## 4) Capture + สร้าง burst traffic (Part C)
```
# บน h2 (ก่อน apply TBF)
h2# tcpdump -i h2-eth0 -w before_shaping.pcap &

# บน h1 (รัน traffic generator)
h1# python3 generate_burst_traffic.py

# หยุด capture บน h2
h2# kill %1

# --- apply TBF ตาม Part B บน h1 แล้วรันซ้ำ ---

h2# tcpdump -i h2-eth0 -w after_shaping.pcap &
h1# python3 generate_burst_traffic.py
h2# kill %1
```

## 4.5) รัน Leaky Bucket implementation เอง (Part D — จำเป็นสำหรับกลุ่ม G19)
```
python3 leaky_bucket_shaper.py
```
สังเกต log `[SEND @ ...]` — ควรห่างกันคงที่ที่ประมาณ `1/23 ≈ 0.043` วินาที
ไม่ว่า input จะยิงเข้ามาถี่แค่ไหน (ตรงข้ามกับ Token Bucket ที่ยอม burst ได้)
บันทึกจำนวน `sent` และ `dropped` ที่สรุปท้าย log ไว้ในรายงานด้วย

## 5) วิเคราะห์ด้วย Wireshark (Part E)
1. เปิด `before_shaping.pcap` และ `after_shaping.pcap`
2. Statistics → IO Graph → ตั้งค่า Y-axis เป็น **Bits/Tick**, interval **10 ms**
3. เปรียบเทียบกราฟทั้งสองไฟล์ — สังเกต pattern ของ throughput
4. บันทึกภาพกราฟทั้งสองไว้ในรายงาน
5. คำนวณ jitter: Statistics → Flow Graph หรือ export timestamp ด้วย
   File → Export Packet Dissections → As CSV แล้วคำนวณส่วนเบี่ยงเบนมาตรฐาน
   ของ inter-arrival time ด้วย Python/Excel

## ข้อควรระวัง
การทดลองนี้ทำใน Mininet (virtual network) เท่านั้น ห้ามนำเทคนิคสร้าง traffic
แบบ burst จำนวนมากไปทดสอบกับเครือข่ายจริงหรือเครือข่ายขององค์กรอื่นโดยไม่ได้รับอนุญาต
เนื่องจากอาจถูกตีความเป็นการโจมตีแบบ Denial of Service (DoS)
