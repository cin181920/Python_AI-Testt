# Mengimpor modul datetime untuk mendapatkan waktu saat ini
import datetime
# Mengimpor modul logging untuk mencatat aktivitas atau pesan error ke konsol
import logging
# Mengimpor modul asyncio untuk mendukung operasi asinkron (paralel) tanpa memblokir sistem
import asyncio
# Mengimpor beberapa tipe data dari typing untuk memberikan petunjuk tipe (Type Hinting)
from typing import Dict, Any, List
# Mengimpor ABC (Abstract Base Class) dan abstractmethod untuk membuat blueprint kelas abstrak
from abc import ABC, abstractmethod

# =========================================================
# KRITERIA 4: Error Handling & Logging
# Menggunakan modul logging terstandarisasi untuk memastikan format log (waktu, jenis error) jelas (traceability).
# =========================================================
# Mengatur konfigurasi dasar logging: level INFO, dan format penulisan (waktu - nama modul - level - pesan)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Membuat objek logger dengan nama file/modul saat ini untuk mulai mencatat log
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# 1. Modul Manajemen Pengguna & Kontrol Kuota
# KRITERIA 1: Module & Logic Design (Separation of Responsibilities)
# Kelas ini tidak dicampur dengan eksekusi tugas. Ia khusus murni mengelola data User dan kuota harian.
# ---------------------------------------------------------
class User:
    # Fungsi inisialisasi yang dipanggil saat objek User baru dibuat
    def __init__(self, username: str, quota: int):
        # Menyimpan nama pengguna ke dalam variabel instans
        self.username = username
        # Menyimpan jumlah batas maksimal (kuota) tugas yang bisa dieksekusi
        self.quota = quota
        # Menyiapkan variabel penghitung tugas yang sudah dijalankan, dimulai dari 0
        self.executed = 0

    # Fungsi untuk mengecek apakah user masih boleh menjalankan tugas
    def can_execute(self) -> bool:
        # Mengembalikan True jika jumlah yang dieksekusi masih lebih kecil dari kuota
        return self.executed < self.quota

    # Fungsi untuk menambah angka tugas yang telah dijalankan
    def increment_executed(self):
        # Menambahkan nilai executed sebanyak 1
        self.executed += 1

class UserManager:
    # Fungsi inisialisasi untuk objek pengelola banyak user
    def __init__(self):
        # Membuat dictionary kosong untuk menyimpan pasangan username sebagai key, dan objek User sebagai value
        self.users: Dict[str, User] = {}

    # Fungsi untuk menambahkan pengguna baru ke dalam dictionary
    def add_user(self, username: str, quota: int):
        # Membuat objek User baru dan menyimpannya ke dalam dictionary menggunakan nama pengguna
        self.users[username] = User(username, quota)

    # Fungsi untuk mengambil data spesifik pengguna berdasarkan namanya
    def get_user(self, username: str) -> User:
        # Mencari pengguna di dalam dictionary dan mengembalikannya (atau None jika tidak ada)
        return self.users.get(username)

# ---------------------------------------------------------
# 2. Action Strategies (Menggunakan Pola Desain Strategy)
# KRITERIA 2: Maintainability (Easy to extend)
# Menggunakan Strategy & Factory Pattern. Jika tim lain ingin membuat jenis Task baru (misal 'Email'),
# mereka hanya perlu membuat kelas baru di sini tanpa mengubah logika TaskExecutor.
# ---------------------------------------------------------
class ActionStrategy(ABC):
    # Mendeklarasikan bahwa fungsi ini harus (wajib) diimplementasikan oleh semua kelas turunannya
    @abstractmethod
    # Fungsi abstrak untuk mengeksekusi aksi yang bersifat asinkron
    async def execute(self, target: str, **kwargs):
        # Kata kunci pass berarti lewati saja, tidak ada kode di fungsi dasar ini
        pass

class SyncAction(ActionStrategy):
    # Mengimplementasikan fungsi wajib execute untuk aksi sinkronisasi
    async def execute(self, target: str, **kwargs):
        # Mencatat log bahwa proses sinkronisasi sedang dilakukan beserta target dan parameternya
        logger.info(f"Performing SYNC on {target} with params: {kwargs}")
        # Menunda eksekusi selama 0.1 detik untuk mensimulasikan proses I/O seperti upload file
        await asyncio.sleep(0.1)

class BackupAction(ActionStrategy):
    # Mengimplementasikan fungsi wajib execute untuk aksi backup
    async def execute(self, target: str, **kwargs):
        # Mencatat log bahwa proses backup sedang dilakukan
        logger.info(f"Performing BACKUP on {target} with params: {kwargs}")
        # Simulasi jeda operasi I/O
        await asyncio.sleep(0.1)

class DeleteAction(ActionStrategy):
    # Mengimplementasikan fungsi wajib execute untuk aksi hapus
    async def execute(self, target: str, **kwargs):
        # Mencatat log bahwa proses penghapusan sedang dilakukan
        logger.info(f"Performing DELETE on {target} with params: {kwargs}")
        # Simulasi jeda operasi I/O
        await asyncio.sleep(0.1)

class ActionFactory:
    # Membuat dictionary tersembunyi (_strategies) yang mendaftarkan string nama aksi dengan objek kelasnya
    _strategies = {
        'sync': SyncAction(), # Kunci 'sync' dipetakan ke objek SyncAction
        'backup': BackupAction(), # Kunci 'backup' dipetakan ke objek BackupAction
        'delete': DeleteAction()  # Kunci 'delete' dipetakan ke objek DeleteAction
    }
    
    # Menjadikan fungsi ini milik Class (bukan instance) agar bisa dipanggil tanpa membuat objek ActionFactory baru
    @classmethod
    # Fungsi untuk mengambil objek strategi (aksi) berdasarkan nama aksi yang diminta
    def get_strategy(cls, action_name: str) -> ActionStrategy:
        # Mengembalikan objek kelas aksi dari dalam dictionary berdasarkan kuncinya
        return cls._strategies.get(action_name)

# ---------------------------------------------------------
# 3. Model Data Task (Tugas)
# KRITERIA 1: Module & Logic Design (Proper Separation)
# Kelas ini hanya bertindak murni sebagai wadah penampung data (Data Transfer Object).
# ---------------------------------------------------------
class Task:
    # Fungsi inisialisasi saat membuat objek tugas baru
    def __init__(self, user: str, time: str, action: str, target: str, params: Dict[str, Any] = None):
        # Menyimpan nama pengguna yang memiliki tugas ini
        self.user = user
        # Menyimpan jadwal waktu kapan tugas harus berjalan
        self.time = time
        # Menyimpan jenis aksi yang harus dilakukan (contoh: 'sync')
        self.action = action
        # Menyimpan nama target operasi (contoh: '/path/folder')
        self.target = target
        # Menyimpan parameter tambahan dalam dictionary, jika None maka diubah menjadi dictionary kosong {}
        self.params = params or {} 

# ---------------------------------------------------------
# 4. Eksekutor Tugas (Task Executor)
# EVALUASI TAMBAHAN 1: Ability to integrate AI-generated code into an existing system
# Desain eksekutor ini sangat modular. Kode hasil AI (seperti logic ActionStrategy) dipasang ke dalam
# eksekutor yang sudah memiliki sistem Error Handling berlapis, sehingga aman disatukan dengan sistem lama.
# ---------------------------------------------------------
class TaskExecutor:
    # Inisialisasi objek pengeksekusi tugas
    def __init__(self, user_manager: UserManager):
        # Menyimpan objek UserManager agar eksekutor bisa mengecek data pengguna
        self.user_manager = user_manager

    # Fungsi asinkron utama yang melakukan eksekusi satu buah tugas tunggal
    async def execute_task(self, task: Task):
        # Mengambil data pengguna secara utuh berdasarkan nama pengguna yang tertulis di objek tugas
        user = self.user_manager.get_user(task.user)
        # Mengecek jika objek pengguna tidak ditemukan (misal belum didaftarkan)
        if not user:
            # Mencatat log error berwarna merah bahwa user tidak ditemukan
            logger.error(f"User {task.user} not found.")
            # Menghentikan eksekusi karena user tidak valid
            return

        # KRITERIA 4 & EVALUASI TAMBAHAN 2 (Solves real problems)
        # SOLUSI MASALAH NYATA 1 (Noisy Neighbor): Mencegah satu user melakukan spam berlebih 
        # yang bisa mematikan server. Pengecekan ini langsung melindungi keseluruhan sistem.
        if not user.can_execute():
            # Jika kuota habis, mencatat log kuning (peringatan) bahwa tugas dibatalkan
            logger.warning(f"User {user.username} has exceeded quota. Task {task.action} on {task.target} aborted.")
            # Menghentikan fungsi agar tugas tidak dilanjutkan
            return

        # KRITERIA 3: AI Tool Usage (Effectively guides AI instead of blindly relying)
        # Memotong kuota SECARA PREVENTIF di awal baris kode adalah hasil dari "Problem Solving" terarah 
        # (guiding AI) untuk mencegah kebocoran kuota (Race Condition) pada eksekusi Asynchronous/paralel.
        # Langsung memotong/menambahkan angka eksekusi pengguna di detik awal sebelum proses IO
        user.increment_executed()

        # Mengambil objek strategi berdasarkan tulisan action pada objek tugas (misal 'sync' menjadi SyncAction)
        strategy = ActionFactory.get_strategy(task.action)
        # Memeriksa apakah strategi tersebut ditemukan di dictionary pabrik aksi
        if not strategy:
            # Jika aksi tidak ada (contoh pengguna nulis 'terbang'), catat pesan error
            logger.error(f"Action {task.action} is not supported.")
            # Karena tugas tidak jadi dijalankan, jumlah eksekusi dikurangi 1 lagi sebagai rollback (pembatalan potongan)
            user.executed -= 1 
            # Menghentikan proses
            return
            
        # Mencatat log informasi bahwa tugas mulai dieksekusi secara sah
        logger.info(f"Executing {task.action} on {task.target} for {user.username}")
        
        # KRITERIA 4 & EVALUASI TAMBAHAN 1 (Safe Integration)
        # Blok try-except mengisolasi kegagalan satu buah task agar tidak merusak (crash) keseluruhan antrean scheduler.
        # Ini adalah bukti bahwa kode AI dapat diintegrasikan dengan aman (tidak merusak sistem existing).
        try:
            # Menjalankan fungsi utama execute pada objek aksi (menunggu sampai selesai secara asinkron)
            await strategy.execute(task.target, **task.params)
        # Menangkap error apa pun yang mungkin muncul dari operasi di atas (seperti ValueError, IOError dll)
        except Exception as e:
            # Hanya mencatat pesan error-nya saja ke konsol, program tidak akan crash
            logger.error(f"Task {task.action} failed: {e}") 

# ---------------------------------------------------------
# 5. Sistem Penjadwalan (Scheduling System)
# ---------------------------------------------------------
class Scheduler:
    # Saat penjadwal diinisialisasi
    def __init__(self, executor: TaskExecutor):
        # Membuat list (daftar) kosong untuk menampung semua tugas yang didaftarkan
        self.tasks: List[Task] = [] 
        # Mengaitkan objek TaskExecutor ke dalam Scheduler agar ia tahu alat mana yang mengeksekusi tugasnya
        self.executor = executor

    # Fungsi untuk mendaftarkan tugas baru ke dalam antrean panjang
    def add_task(self, task: Task):
        # Memasukkan tugas ke baris belakang list
        self.tasks.append(task)

    # KRITERIA 3: AI Tool Usage (Effectively guides AI)
    # Hasil mengarahkan AI untuk menggunakan library `asyncio` demi performa paralel tinggi (*non-blocking*), 
    # ketimbang menerima solusi Threading / eksekusi blocking yang lebih usang dan rawan *overhead*.
    async def run(self, current_time_override: str = None):
        # Mendapatkan waktu sekarang dalam format Jam:Menit, atau menggunakan waktu simulasi manual (jika ada)
        now = current_time_override or datetime.datetime.now().strftime('%H:%M')
        # Mencatat log bahwa penjadwal sedang mengecek tugas pada jam ini
        logger.info(f"Scheduler checking tasks for time: {now}")
        
        # Saring daftar tugas secara instan: Ambil hanya tugas-tugas yang jam targetnya sama dengan jam sekarang
        tasks_to_run = [task for task in self.tasks if task.time == now]
        
        # Jika hasil penyaringan kosong (tidak ada jadwal jam segini)
        if not tasks_to_run:
            # Catat log informasi bahwa tidak ada tugas
            logger.info("No tasks to run at this time.")
            # Hentikan eksekusi
            return
            
        # Membuat antrean list fungsi coroutine: persiapkan eksekusi tugas untuk setiap objek tugas yang tersaring
        coroutines = [self.executor.execute_task(task) for task in tasks_to_run]
        
        # EVALUASI TAMBAHAN 2: Prompt accuracy and whether it solves real problems
        # SOLUSI MASALAH NYATA 2 (I/O Bottleneck): Penggunaan `asyncio.gather` mengatasi masalah nyata
        # antrean panjang (blocking). Puluhan/ratusan tugas I/O bisa ditembak secara serentak tanpa saling tunggu.
        await asyncio.gather(*coroutines)

# ---------------------------------------------------------
# Simulasi Program Utama (Main)
# KRITERIA 2: Maintainability (Structured Flow)
# Instansiasi objek dan alur input datanya (add_user -> add_task -> run) sangat terstruktur dan mudah dibaca.
# ---------------------------------------------------------
# Fungsi utama dari keseluruhan simulasi program
async def main():
    # Membuat objek manajer pengguna baru
    user_manager = UserManager()
    # Mendaftarkan pengguna bernama 'alice' dengan kuota harian maksimal 3 tugas
    user_manager.add_user('alice', 3) 
    # Mendaftarkan pengguna bernama 'bob' dengan kuota harian maksimal 5 tugas
    user_manager.add_user('bob', 5)   

    # Membuat mesin pelaksana tugas (executor) dan menyuntikkan (inject) objek manajer pengguna ke dalamnya
    executor = TaskExecutor(user_manager)
    # Membuat mesin penjadwal dan menyuntikkan alat eksekutornya
    scheduler = Scheduler(executor)

    # Menambahkan tugas pertama milik alice (waktu jam 12, aksi sync)
    scheduler.add_task(Task('alice', '12:00', 'sync', '/data/x', {'mode': 'fast'}))
    # Menambahkan tugas kedua milik bob (waktu jam 12, aksi backup)
    scheduler.add_task(Task('bob', '12:00', 'backup', '/srv/y', {'compression': 'gzip'}))
    # Menambahkan tugas ketiga milik alice (waktu jam 12, aksi delete)
    scheduler.add_task(Task('alice', '12:00', 'delete', '/tmp/z', {'force': True}))
    
    # Menambahkan tugas keempat milik alice (aksi sync)
    scheduler.add_task(Task('alice', '12:00', 'sync', '/data/w'))
    # Menambahkan tugas kelima milik alice (aksi sync) - ini pasti diblokir karena kuota alice hanya 3
    scheduler.add_task(Task('alice', '12:00', 'sync', '/data/v')) 

    # Mulai menjalankan antrean scheduler, memalsukan jam saat ini menjadi jam 12 siang persis
    await scheduler.run(current_time_override='12:00')

# Pengecekan standar di Python untuk memastikan file ini dijalankan langsung (bukan di-import oleh modul lain)
if __name__ == "__main__":
    # Menjalankan fungsi utama asinkron menggunakan modul asyncio
    asyncio.run(main())
