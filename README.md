# PesanKoe (PitonKoeAppChat)
Program untuk berbagi pesan antar perangkat dalam satu jaringan yang sama menggunakan Python dengan cara yang SIGMA
W.I.P

Fitur
1. **Pesan Privat** (TO:target_id: pesan)
2. **Broadcast** (ALL:pesan ke semua client)
3. **RTT Measurement** (waktu respons dalam ms)
4. **ASCII Code Display** di setiap pesan
5. **Auto-log** ke file `klien_{ID}_log.txt`
6. **Input validation** (ID/host tidak boleh kosong)
7. **Connection retry** saat host salah
8. **Timestamp** real-time

Requirement
1. Komputer (Tentu Saja)
2. Python
3. Tkinter

How To Use
### 1. Clone repo
git clone https://github.com/kanashifumiku/PesanKoeAppChat.git
cd PesanKoeAppChat

### 2. Jalankan Server (satu terminal)
python Peladen.py

### 3. Jalankan Client (terminal lain, tiap device)
python Klien.py

### 4. Koneksi
Pastikan setiap perangkat terhubung ke satu jaringan yang sama. Bebas mau via kabel / nirkabel. Internet? Gak perlu.

Rencana Penambahan Fitur Selanjutnya...
### 1. Penambahan fitur transfer file antar perangkat.
### 2. Perbaikan UI/UX

