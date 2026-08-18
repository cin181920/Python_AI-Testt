# Python AI Test - Evaluation & Refactoring

Evaluasi arsitektur sistem Task Scheduler asinkron:

## 1. Desain Prompt Refactoring
- **Konteks:** Menjelaskan ini adalah sistem Task Scheduler Python.
- **Pola Desain:** Menginstruksikan penerapan prinsip SOLID (*Strategy* & *Factory Pattern*) untuk menghindari *if-else* bercabang.
- **Batasan Teknis:** Wajib menggunakan `asyncio` untuk operasi I/O dan validasi kuota secara preventif.

## 2. Penolakan Saran AI
- **Database Kompleks:** Saran ORM/PostgreSQL ditolak karena *in-memory* dictionary sudah cukup untuk tahap purwarupa.
- **Penanganan Error Buruk:** Saran blok `try-except` kosong (*pass*) ditolak, diganti kewajiban memakai modul `logging`.
- **Multithreading:** Ditolak, dialihkan ke `asyncio` murni karena lebih ringan untuk proses I/O tertunda.

## 3. Strategi Skalabilitas Skala Besar
- **Message Broker:** Pindahkan antrean dari memori ke RabbitMQ/Kafka/Celery.
- **Horizontal Scaling:** Pecah *TaskExecutor* menjadi *worker nodes* terdistribusi (misal via Kubernetes).
- **Distributed Cache:** Gunakan Redis untuk validasi kuota (*Rate Limiting*) berkecepatan tinggi.
- **Database:** Simpan data user dan riwayat eksekusi ke PostgreSQL/MongoDB.

## 4. Modul Reusable (Bisa Dipakai Tim Lain)
- **Modul Kuota & Rate Limiting:** Bisa dijadikan layanan otorisasi (*Auth/Quota Service*) terpusat.
- **Action Strategy Framework:** Bisa dijadikan SDK internal agar tim lain mudah membuat tipe *task* kustom tanpa mengubah kode eksekutor utama.

## 5. Integrasi Kode AI ke Sistem Existing
- **Standarisasi:** Menyesuaikan struktur (OOP) dan penamaan dengan konvensi internal.
- **Isolasi Kegagalan:** Eksekusi tugas dibungkus `try-except` agar jika kode AI gagal, sistem utama tidak *crash*.
- **Mekanisme Rollback:** Kuota dipotong sebelum eksekusi, namun dikembalikan (*rollback*) jika jenis tugas tidak valid.

## 6. Akurasi Prompt & Penyelesaian Masalah
- **Prompt Terarah:** Sangat spesifik menargetkan *asyncio*, validasi limitasi, dan *extensibility*.
- **Solusi Masalah Nyata:**
  1. Mengatasi *Noisy Neighbor* (mencegah satu user memonopoli resource server).
  2. Mengatasi *Blocking I/O* (memungkinkan eksekusi banyak *network/disk process* secara paralel).

## 7. Analisis Optimalitas Arsitektur
Arsitektur ini **sangat optimal untuk skala aplikasi tunggal (purwarupa)**, namun memiliki beberapa hambatan untuk skala sistem terdistribusi.

### ✅ Kelebihan (Optimalitas Saat Ini):
- **Efisiensi I/O:** Memakai `asyncio.gather` sehingga ratusan tugas berjalan paralel tanpa memboroskan memori *Thread*.
- **Pencarian O(1):** Penggunaan struktur data *Dictionary* membuat pencarian data User dan strategi aksi menjadi instan.
- **Validasi Fail-Fast:** Kuota dicek di paling awal, menghemat *resource* sistem dari memproses tugas yang ujungnya ditolak.

### ❌ Kekurangan (Bottleneck Skala Besar) & Solusinya:
- **Pencarian Jadwal Linear (O(N)):** Memfilter list jadwal satu per satu akan sangat lambat jika ada jutaan tugas. **Solusi:** Gunakan *Priority Queue (Min-Heap)*.
- **Data Volatile:** Antrean dan kuota hilang total jika server mati (hanya tersimpan di RAM). **Solusi:** Migrasi penyimpanan ke *Message Broker* (RabbitMQ) dan Database.
- **Tanpa Mekanisme Retry:** Tugas yang gagal dibiarkan begitu saja. **Solusi:** Tambahkan antrean khusus *Dead Letter Queue (DLQ)* dan *Exponential Backoff Retry*.
- **Rawan Event Loop Blocking:** Satu tugas komputasi berat (CPU-bound) akan membekukan seluruh antrean *asyncio*. **Solusi:** Lempar komputasi berat ke *worker* atau proses terpisah.
