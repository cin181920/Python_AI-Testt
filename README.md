# Python AI Test - Evaluation & Refactoring

Kode dalam repositori ini merupakan hasil simulasi dan refactoring sistem penjadwalan dan pengeksekusi tugas (Task Scheduling & Execution System) secara asinkron dengan pembatasan kuota pengguna.

Berikut adalah evaluasi dan penjelasan terkait arsitektur sistem:

## 1. How did you design your prompts to guide AI for refactoring?

Saya merancang *prompt* dengan pendekatan yang terstruktur, tidak sekadar meminta AI "memperbaiki kode". Langkah-langkah yang saya gunakan meliputi:
1. **Memberikan Konteks & Tujuan:** Saya menjelaskan bahwa ini adalah sistem penjadwalan tugas (Task Scheduler) berbasis Python.
2. **Menentukan Pola Desain (Design Patterns):** Daripada membiarkan AI menggunakan banyak *if-else* untuk jenis tugas, saya secara eksplisit meminta penerapan prinsip SOLID, khususnya *Open/Closed Principle*. Saya meminta AI menggunakan **Strategy Pattern** dan **Factory Pattern** untuk mengeksekusi *Action* (seperti `Sync`, `Backup`, `Delete`).
3. **Menetapkan Batasan Teknis:** Saya memerintahkan AI agar menggunakan `asyncio` karena operasi *task* umumnya bersifat *I/O bound*, dan menyertakan logika pengecekan kuota di awal (preventif) guna menghindari *race conditions*.

## 2. Did you reject any AI-generated suggestions? Why?

Ya, saya menolak beberapa saran awal dari AI karena tidak sesuai dengan skala purwarupa (*prototype*) atau prinsip *best practice*. Beberapa di antaranya:
* **Penggunaan Database yang Terlalu Kompleks:** AI sempat menyarankan integrasi dengan ORM (seperti SQLAlchemy) dan SQLite/PostgreSQL untuk menyimpan *User* dan *Task*. Saya menolaknya karena untuk tahap ini, menyimpan state di memori (*in-memory dictionary/list*) sudah cukup untuk mendemonstrasikan logika.
* **Penanganan Error (Error Handling) yang Buruk:** AI sempat memberikan blok `try-except` yang menangkap (`pass`) semua error secara diam-diam. Saya menolaknya dan menginstruksikan AI untuk menambahkan modul `logging` agar setiap kegagalan *task* terekam secara jelas tanpa mematikan seluruh program.
* **Multithreading vs Asyncio:** AI sempat menyarankan `concurrent.futures.ThreadPoolExecutor`. Saya memintanya mengganti ke `asyncio` murni karena lebih ringan untuk simulasi operasi jaringan/IO yang tertunda (*sleep*).

## 3. If this system needs to handle tens of thousands of tasks daily, how would you scale the architecture?

Arsitektur *in-memory* saat ini tidak akan bertahan untuk skala tersebut. Untuk *scaling*, saya akan merombak arsitekturnya menjadi sistem terdistribusi:
1. **Message Broker / Task Queue:** Saya akan mengeluarkan tugas dari *list* memori dan memasukkannya ke sistem antrean seperti **RabbitMQ**, **Apache Kafka**, atau menggunakan **Celery** (dengan backend Redis). Ini mencegah tugas hilang saat server *restart*.
2. **Horizontal Scaling (Worker Nodes):** Modul `TaskExecutor` akan dipisahkan menjadi *microservice* mandiri (*worker*). Kita bisa menjalankan puluhan *container* worker (via Kubernetes) yang akan menarik (*consume*) tugas dari antrean secara paralel.
3. **Distributed Caching untuk Kuota:** Pengecekan `can_execute()` akan membebani database jika ditanyakan ribuan kali per detik. Saya akan menggunakan **Redis** untuk mengimplementasikan algoritma *Rate Limiting* (seperti *Token Bucket* atau *Sliding Window*) agar pengecekan kuota sangat cepat dan tersinkronisasi antar *worker*.
4. **Database Persisten:** Data User dan log eksekusi Task akan disimpan di database persisten (seperti PostgreSQL atau MongoDB) untuk keperluan audit.

## 4. Which parts would you extract into reusable modules for other teams?

Berdasarkan kode yang ada, ada dua komponen utama yang sangat cocok dijadikan *library* internal atau *microservice* agar bisa digunakan oleh tim lain:
1. **Sistem Manajemen Kuota (User Quota & Rate Limiting Module):** Logika pada kelas `User` dan `UserManager` (mengecek sisa kuota, memotong kuota) sangat generik. Ini bisa diekstrak menjadi layanan otorisasi (*Auth & Quota Service*) terpusat, sehingga tim pengembangan fitur lain tidak perlu membuat logika pembatasan limit mereka sendiri.
2. **Action Strategy Framework:** Kelas `ActionStrategy` (sebagai Interface/Abstract Base Class) dan `ActionFactory` bisa dijadikan semacam **SDK (Software Development Kit)** internal. Dengan mengekstrak bagian ini, tim lain dapat membuat jenis *task* mereka sendiri (misalnya `SendEmailAction` atau `GenerateReportAction`) cukup dengan mewarisi kelas `ActionStrategy` tanpa harus mengganggu, memahami, atau mengubah inti dari mesin eksekutor (`TaskExecutor`).

## 5. Ability to integrate AI-generated code into an existing system

Proses integrasi kode AI ke sistem *existing* tidak dilakukan dengan *copy-paste* mentah, melainkan melalui tahap adaptasi dan pengamanan (safety measures):
* **Standarisasi & Refactoring:** Kode awal dari AI sering kali menggunakan penamaan variabel atau struktur yang tidak konsisten dengan sistem lama. Saya memodifikasinya agar sesuai dengan konvensi kode (misalnya mengubah fungsi biasa menjadi kelas OOP menggunakan `ActionStrategy`) agar bisa 'dipasang' dengan rapi ke arsitektur lama tanpa menimbulkan konflik.
* **Isolasi Kegagalan (Fault Isolation):** AI sering lupa memikirkan skenario terburuk. Oleh karena itu, pada metode `execute_task`, saya membungkus eksekusi AI ke dalam blok `try-except` dan memasang `logger`. Tujuannya, jika kode aksi (Action) gagal, sistem *scheduler* utama tidak ikut *crash*.
* **Penanganan State (Rollback Mechanism):** Saya memodifikasi logika AI pada bagian pemotongan kuota. Kuota dipotong *sebelum* tugas berjalan (preventif terhadap *race condition*). Jika tugas gagal karena kelas aksi tidak didukung, saya menambahkan logika untuk mengembalikan kuota (*rollback*) `user.executed -= 1`, memastikan integrasi kode AI tidak merusak akurasi data di sistem lama.

## 6. Prompt accuracy and whether it solves real problems

Untuk memastikan AI menghasilkan solusi yang relevan, akurasi *prompt* adalah kuncinya. 
* **Akurasi Prompt:** Saya membuat *prompt* yang menargetkan masalah spesifik: *"Buatkan sistem Task Executor di Python menggunakan asyncio. Sistem ini HARUS memvalidasi kuota harian user sebelum eksekusi, dan harus mudah ditambahkan jenis task baru tanpa mengubah core logic (gunakan pattern yang tepat)"*. Ketepatan instruksi ini mencegah AI membuat iterasi kode yang tidak berguna.
* **Menyelesaikan Masalah Nyata (Real Problems):** Hasil dari integrasi ini secara langsung menyelesaikan dua masalah nyata (pain points) di level produksi:
  1. **Menghindari *Noisy Neighbor Problem*:** Modul `User Management & Quota` memastikan tidak ada satu klien pun yang bisa melakukan *spamming* dan menghabiskan *resource* server (mencegah *Denial of Service* secara internal).
  2. **Mengatasi Bottleneck (Blocking I/O):** Dengan memaksa AI menggunakan eksekusi asinkron (`asyncio.gather`), sistem berubah dari yang tadinya memproses tugas satu per satu (*blocking*) menjadi mampu menangani ratusan proses I/O secara paralel pada waktu yang bersamaan.
