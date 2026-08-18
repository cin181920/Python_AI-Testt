import datetime
import logging
import asyncio
from typing import Dict, Any, List
from abc import ABC, abstractmethod

# Konfigurasi Logging (untuk mencatat log/aktivitas program ke layar)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# 1. Modul Manajemen Pengguna & Kontrol Kuota
# ---------------------------------------------------------
class User:
    """Kelas untuk merepresentasikan pengguna di dalam sistem."""
    def __init__(self, username: str, quota: int):
        self.username = username  # Nama pengguna (contoh: 'alice')
        self.quota = quota        # Batas maksimal tugas yang diizinkan (contoh: 3)
        self.executed = 0         # Jumlah tugas yang sudah dijalankan saat ini

    def can_execute(self) -> bool:
        """Mengecek apakah pengguna masih memiliki sisa kuota untuk menjalankan tugas."""
        return self.executed < self.quota

    def increment_executed(self):
        """Menambah jumlah tugas yang telah dieksekusi oleh pengguna."""
        self.executed += 1

class UserManager:
    """Kelas untuk mengelola kumpulan pengguna (User)."""
    def __init__(self):
        self.users: Dict[str, User] = {} # Dictionary untuk menyimpan objek User berdasarkan username

    def add_user(self, username: str, quota: int):
        """Mendaftarkan pengguna baru dengan batas kuotanya."""
        self.users[username] = User(username, quota)

    def get_user(self, username: str) -> User:
        """Mengambil data pengguna berdasarkan username-nya."""
        return self.users.get(username)

# ---------------------------------------------------------
# 2. Action Strategies (Menggunakan Pola Desain Strategy)
# ---------------------------------------------------------
class ActionStrategy(ABC):
    """Kelas dasar abstrak (Abstract Base Class) untuk semua tipe aksi."""
    @abstractmethod
    async def execute(self, target: str, **kwargs):
        """Setiap aksi wajib memiliki fungsi execute ini."""
        pass

class SyncAction(ActionStrategy):
    """Aksi untuk melakukan sinkronisasi data."""
    async def execute(self, target: str, **kwargs):
        logger.info(f"Performing SYNC on {target} with params: {kwargs}")
        await asyncio.sleep(0.1) # Simulasi proses IO/jaringan yang memakan waktu 0.1 detik

class BackupAction(ActionStrategy):
    """Aksi untuk melakukan backup data."""
    async def execute(self, target: str, **kwargs):
        logger.info(f"Performing BACKUP on {target} with params: {kwargs}")
        await asyncio.sleep(0.1)

class DeleteAction(ActionStrategy):
    """Aksi untuk menghapus data."""
    async def execute(self, target: str, **kwargs):
        logger.info(f"Performing DELETE on {target} with params: {kwargs}")
        await asyncio.sleep(0.1)

class ActionFactory:
    """Factory (Pabrik) untuk memilih jenis kelas Aksi secara dinamis."""
    _strategies = {
        'sync': SyncAction(),
        'backup': BackupAction(),
        'delete': DeleteAction()
    }
    
    @classmethod
    def get_strategy(cls, action_name: str) -> ActionStrategy:
        """Mengambil objek aksi yang sesuai dengan string action_name."""
        return cls._strategies.get(action_name)

# ---------------------------------------------------------
# 3. Model Data Task (Tugas)
# ---------------------------------------------------------
class Task:
    """Kelas untuk menampung informasi sebuah tugas."""
    def __init__(self, user: str, time: str, action: str, target: str, params: Dict[str, Any] = None):
        self.user = user       # Siapa yang menjalankan tugas
        self.time = time       # Kapan tugas harus dijalankan (format jam:menit)
        self.action = action   # Jenis tugas (sync, backup, delete)
        self.target = target   # Target folder/file dari tugas
        self.params = params or {} # Parameter tambahan dalam bentuk kamus (dictionary)

# ---------------------------------------------------------
# 4. Eksekutor Tugas (Task Executor)
# ---------------------------------------------------------
class TaskExecutor:
    """Kelas yang bertanggung jawab menjalankan tugas dengan memvalidasi kuota terlebih dahulu."""
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

    async def execute_task(self, task: Task):
        """Fungsi asinkron untuk mengeksekusi sebuah tugas."""
        user = self.user_manager.get_user(task.user)
        if not user:
            logger.error(f"User {task.user} not found.") # Jika user tidak terdaftar
            return

        # Pengecekan kuota
        if not user.can_execute():
            logger.warning(f"User {user.username} has exceeded quota. Task {task.action} on {task.target} aborted.")
            return

        # Potong kuota di awal untuk mencegah "Race Condition" pada eksekusi asinkron serentak
        user.increment_executed()

        # Ambil strategi/cara pengeksekusian tugas
        strategy = ActionFactory.get_strategy(task.action)
        if not strategy:
            logger.error(f"Action {task.action} is not supported.")
            user.executed -= 1 # Rollback (kembalikan) kuota karena tugas dibatalkan
            return
            
        logger.info(f"Executing {task.action} on {task.target} for {user.username}")
        try:
            # Jalankan tugas sesuai strateginya beserta parameternya
            await strategy.execute(task.target, **task.params)
        except Exception as e:
            logger.error(f"Task {task.action} failed: {e}") # Tangkap dan log pesan error jika gagal
            # Opsional: Kembalikan kuota jika eksekusi gagal di tengah jalan
            # user.executed -= 1

# ---------------------------------------------------------
# 5. Sistem Penjadwalan (Scheduling System)
# ---------------------------------------------------------
class Scheduler:
    """Kelas untuk mengelola antrean tugas dan menjadwalkan kapan tugas dieksekusi."""
    def __init__(self, executor: TaskExecutor):
        self.tasks: List[Task] = [] # Daftar / List tugas
        self.executor = executor

    def add_task(self, task: Task):
        """Fungsi untuk menambahkan tugas ke dalam antrean."""
        self.tasks.append(task)

    async def run(self, current_time_override: str = None):
        """Fungsi utama untuk menjalankan tugas yang sudah waktunya dieksekusi."""
        # Ambil waktu sekarang, atau gunakan waktu simulasi jika current_time_override diisi
        now = current_time_override or datetime.datetime.now().strftime('%H:%M')
        logger.info(f"Scheduler checking tasks for time: {now}")
        
        # Saring dan ambil semua tugas yang jadwalnya sesuai dengan waktu saat ini
        tasks_to_run = [task for task in self.tasks if task.time == now]
        
        if not tasks_to_run:
            logger.info("No tasks to run at this time.")
            return
            
        # Kumpulkan semua coroutine (fungsi asinkron) ke dalam satu wadah
        coroutines = [self.executor.execute_task(task) for task in tasks_to_run]
        
        # Eksekusi secara serentak (paralel/asinkron) agar tidak saling menunggu
        await asyncio.gather(*coroutines)

# ---------------------------------------------------------
# Simulasi Program Utama (Main)
# ---------------------------------------------------------
async def main():
    # Setup awal manajemen user
    user_manager = UserManager()
    user_manager.add_user('alice', 3) # Alice punya kuota 3
    user_manager.add_user('bob', 5)   # Bob punya kuota 5

    # Siapkan eksekutor dan penjadwalnya
    executor = TaskExecutor(user_manager)
    scheduler = Scheduler(executor)

    # Menambahkan beberapa tugas (lengkap dengan parameternya)
    scheduler.add_task(Task('alice', '12:00', 'sync', '/data/x', {'mode': 'fast'}))
    scheduler.add_task(Task('bob', '12:00', 'backup', '/srv/y', {'compression': 'gzip'}))
    scheduler.add_task(Task('alice', '12:00', 'delete', '/tmp/z', {'force': True}))
    
    # Task ekstra untuk mendemonstrasikan penolakan karena limit kuota (Alice hanya punya 3)
    scheduler.add_task(Task('alice', '12:00', 'sync', '/data/w'))
    scheduler.add_task(Task('alice', '12:00', 'sync', '/data/v')) # Tugas ini pasti ditolak

    # Jalankan Scheduler (Simulasi waktu dimajukan ke jam 12:00)
    await scheduler.run(current_time_override='12:00')

# Titik masuk program (Entry point)
if __name__ == "__main__":
    asyncio.run(main())
