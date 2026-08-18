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
