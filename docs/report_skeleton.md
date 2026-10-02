# Lab 14: Traffic Shaping ด้วย Token Bucket และ Leaky Bucket

**รหัสกลุ่ม:** G19
**Algorithm ที่ได้รับ:** leaky_bucket

---

## 1. ค่า Parameter ประจำกลุ่ม

รันจาก `generate_group_params.py G19`:

| Parameter | ค่า |
|---|---|
| bandwidth_mbps | 2 |
| token_rate_kbit | 256 |
| bucket_size_kbit | 32 |
| burst_size_packets | 97 |
| burst_interval_ms | 500 |
| packet_size_bytes | 1400 |
| algorithm | leaky_bucket |
| latency_ms | 400 |

---

## 2. Part A–B: Topology และการตั้งค่า TBF

- Topology: h1 -- s1 -- h2, bandwidth = 2 Mbps
- คำสั่ง tc ที่ใช้ตั้งค่า TBF บน h1-eth0:
  ```
  tc qdisc add dev h1-eth0 root tbf rate 256kbit burst 32kbit latency 400ms
  ```
- ผลจาก `tc -s qdisc show dev h1-eth0`: _[แปะผลจริง]_

---

## 3. Part C: การสร้าง Bursty Traffic และ Capture

- ไฟล์ที่ได้: `before_shaping.pcap`, `after_shaping.pcap`
- (สรุปสั้นๆ ว่า generate traffic อย่างไร ตรงตาม parameter กลุ่มหรือไม่)

---

## 4. Part D: ผล Implementation Leaky Bucket (จำเป็นสำหรับกลุ่มนี้)

- Parameter ที่ใช้: `drain_rate_pps = 23` (แปลงจาก token_rate_kbit=256, packet_size=1400 bytes),
  `bucket_capacity = 3` (แปลงจาก bucket_size_kbit=32) — สูตรแปลงหน่วยอยู่ใน comment
  ของ `leaky_bucket_shaper.py`
- สรุปผลการรัน: จำนวน sent / dropped _[กรอกผลจริง]_
- เปรียบเทียบ timestamp ของ output ว่าห่างกันคงที่ตาม drain_rate (≈0.043 วินาที) หรือไม่
- อธิบายว่าทำไม dropped สูง (buffer เล็กแค่ 3 packets ชนกับ burst 97 packets ที่ยิงเข้ามาถี่)

---

## 5. Part E: ผลการวิเคราะห์ด้วย Wireshark

| Metric | Before Shaping | After Shaping |
|---|---|---|
| Peak throughput (Mbps) | | |
| Average throughput (Mbps) | | |
| Packet loss (%) | | |
| Max inter-arrival delay (ms) | | |
| Jitter (std. dev of delay) | | |

**[แนบภาพ IO Graph ทั้งสองไฟล์ตรงนี้]**

---

## 6. Part F: คำถามวิเคราะห์และอภิปราย

**1) เมื่อเพิ่มขนาด burst ใน TBF (bucket_size_kbit / token_rate_kbit ของกลุ่ม) ให้มากขึ้น ผลลัพธ์ที่เห็นใน Wireshark IO Graph เปลี่ยนไปอย่างไร และเพราะเหตุใด**

_[คำตอบ — อ้างอิงค่าจริงของกลุ่มและกราฟที่วัดได้]_

**2) หากลดค่า rate ให้ต่ำกว่า input traffic rate จริงมาก ๆ จะเกิดอะไรขึ้นกับ packet loss และ latency สังเกตได้จากที่ใดใน capture file**

_[คำตอบ]_

**3) เปรียบเทียบผลลัพธ์ระหว่างกลุ่มที่ได้ algorithm: token_bucket กับกลุ่มที่ได้ algorithm: leaky_bucket — output traffic pattern ต่างกันอย่างไรเมื่อ input เป็น burst เดียวกัน**

_[คำตอบ]_

**4) ในการใช้งานจริง เช่น ISP ที่ทำ bandwidth throttling ควรเลือก Token Bucket หรือ Leaky Bucket และเพราะเหตุใด (พิจารณาจาก traffic ประเภท video streaming เทียบกับ file download)**

_[คำตอบ]_

**5) อธิบายว่าเหตุใดการเพิ่ม bucket_size มากเกินไปอาจทำให้ Token Bucket ไม่ต่างจากไม่มีการ shaping เลย**

_[คำตอบ]_

---

## 7. สรุป

_[สรุปสั้นๆ สิ่งที่เรียนรู้จาก lab นี้]_

---

## สิ่งที่ต้องส่ง (checklist)

- [ ] `before_shaping.pcap` และ `after_shaping.pcap`
- [ ] ตารางค่า parameter ประจำกลุ่ม
- [ ] ตารางบันทึกผลการวัด (Part E) พร้อมภาพ IO Graph ทั้งสองไฟล์
- [ ] คำตอบคำถามวิเคราะห์ทั้ง 5 ข้อ (Part F)
- [ ] Source code ที่แก้ไขแล้ว: `topo_bucket.py`, `generate_burst_traffic.py`, และ `leaky_bucket_shaper.py` (หากได้ algorithm นี้)
- [ ] รูปแบบไฟล์ส่งงาน: PDF report + zip ของ source code และ pcap
