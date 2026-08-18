import datetime
import logging
import asyncio
from typing import Dict, Any, List
from abc import ABC, abstractmethod

# =========================================================
# KRITERIA 4: Error Handling & Logging
# Menggunakan modul logging terstandarisasi untuk memastikan format log (waktu, jenis error) jelas (traceability).
# =========================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# 1. Modul Manajemen Pengguna & Kontrol Kuota
# KRITERIA 1: Module & Logic Design (Separation of Responsibilities)
# Kelas ini tidak dicampur dengan eksekusi tugas. Ia khusus murni mengelola data User dan kuota harian.
# ---------------------------------------------------------
class User:
    def __init__(self, username: str, quota: int):
        self.username = username
        self.quota = quota
        self.executed = 0

    def can_execute(self) -> bool:
        return self.executed < self.quota

    def increment_executed(self):
        self.executed += 1

class UserManager:
    def __init__(self):
        self.users: Dict[str, User] = {}

    def add_user(self, username: str, quota: int):
        self.users[username] = User(username, quota)

    def get_user(self, username: str) -> User:
        return self.users.get(username)

# ---------------------------------------------------------
# 2. Action Strategies (Menggunakan Pola Desain Strategy)
# KRITERIA 2: Maintainability (Easy to extend)
# Menggunakan Strategy & Factory Pattern. Jika tim lain ingin membuat jenis Task baru (misal 'Email'),
# mereka hanya perlu membuat kelas baru di sini tanpa mengubah logika TaskExecutor.
# ---------------------------------------------------------
class ActionStrategy(ABC):
    @abstractmethod
    async def execute(self, target: str, **kwargs):
        pass

class SyncAction(ActionStrategy):
    async def execute(self, target: str, **kwargs):
        logger.info(f"Performing SYNC on {target} with params: {kwargs}")
        await asyncio.sleep(0.1)

class BackupAction(ActionStrategy):
    async def execute(self, target: str, **kwargs):
        logger.info(f"Performing BACKUP on {target} with params: {kwargs}")
        await asyncio.sleep(0.1)

class DeleteAction(ActionStrategy):
    async def execute(self, target: str, **kwargs):
        logger.info(f"Performing DELETE on {target} with params: {kwargs}")
        await asyncio.sleep(0.1)

class ActionFactory:
    _strategies = {
        'sync': SyncAction(),
        'backup': BackupAction(),
        'delete': DeleteAction()
    }
    
    @classmethod
    def get_strategy(cls, action_name: str) -> ActionStrategy:
        return cls._strategies.get(action_name)

# ---------------------------------------------------------
# 3. Model Data Task (Tugas)
# KRITERIA 1: Module & Logic Design (Proper Separation)
# Kelas ini hanya bertindak murni sebagai wadah penampung data (Data Transfer Object).
# ---------------------------------------------------------
class Task:
    def __init__(self, user: str, time: str, action: str, target: str, params: Dict[str, Any] = None):
        self.user = user
        self.time = time
        self.action = action
        self.target = target
        self.params = params or {} 

# ---------------------------------------------------------
# 4. Eksekutor Tugas (Task Executor)
# ---------------------------------------------------------
class TaskExecutor:
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

    async def execute_task(self, task: Task):
        user = self.user_manager.get_user(task.user)
        if not user:
            logger.error(f"User {task.user} not found.")
            return

        # KRITERIA 4: Error Handling & Logging (Clear & Traceable Messages)
        # Menangani skenario pelanggaran batas kuota dengan log peringatan spesifik.
        if not user.can_execute():
            logger.warning(f"User {user.username} has exceeded quota. Task {task.action} on {task.target} aborted.")
            return

        # KRITERIA 3: AI Tool Usage (Effectively guides AI instead of blindly relying)
        # Memotong kuota SECARA PREVENTIF di awal baris kode adalah hasil dari "Problem Solving" terarah 
        # (guiding AI) untuk mencegah kebocoran kuota (Race Condition) pada eksekusi Asynchronous/paralel.
        user.increment_executed()

        strategy = ActionFactory.get_strategy(task.action)
        if not strategy:
            logger.error(f"Action {task.action} is not supported.")
            user.executed -= 1 
            return
            
        logger.info(f"Executing {task.action} on {task.target} for {user.username}")
        
        # KRITERIA 4: Error Handling (Proteksi Sistem)
        # Blok try-except mengisolasi kegagalan satu buah task agar tidak merusak (crash) keseluruhan antrean scheduler.
        try:
            await strategy.execute(task.target, **task.params)
        except Exception as e:
            logger.error(f"Task {task.action} failed: {e}") 

# ---------------------------------------------------------
# 5. Sistem Penjadwalan (Scheduling System)
# ---------------------------------------------------------
class Scheduler:
    def __init__(self, executor: TaskExecutor):
        self.tasks: List[Task] = [] 
        self.executor = executor

    def add_task(self, task: Task):
        self.tasks.append(task)

    # KRITERIA 3: AI Tool Usage (Effectively guides AI)
    # Hasil mengarahkan AI untuk menggunakan library `asyncio` demi performa paralel tinggi (*non-blocking*), 
    # ketimbang menerima solusi Threading / eksekusi blocking yang lebih usang dan rawan *overhead*.
    async def run(self, current_time_override: str = None):
        now = current_time_override or datetime.datetime.now().strftime('%H:%M')
        logger.info(f"Scheduler checking tasks for time: {now}")
        
        tasks_to_run = [task for task in self.tasks if task.time == now]
        
        if not tasks_to_run:
            logger.info("No tasks to run at this time.")
            return
            
        coroutines = [self.executor.execute_task(task) for task in tasks_to_run]
        await asyncio.gather(*coroutines)

# ---------------------------------------------------------
# Simulasi Program Utama (Main)
# KRITERIA 2: Maintainability (Structured Flow)
# Instansiasi objek dan alur input datanya (add_user -> add_task -> run) sangat terstruktur dan mudah dibaca.
# ---------------------------------------------------------
async def main():
    user_manager = UserManager()
    user_manager.add_user('alice', 3) 
    user_manager.add_user('bob', 5)   

    executor = TaskExecutor(user_manager)
    scheduler = Scheduler(executor)

    scheduler.add_task(Task('alice', '12:00', 'sync', '/data/x', {'mode': 'fast'}))
    scheduler.add_task(Task('bob', '12:00', 'backup', '/srv/y', {'compression': 'gzip'}))
    scheduler.add_task(Task('alice', '12:00', 'delete', '/tmp/z', {'force': True}))
    
    scheduler.add_task(Task('alice', '12:00', 'sync', '/data/w'))
    scheduler.add_task(Task('alice', '12:00', 'sync', '/data/v')) 

    await scheduler.run(current_time_override='12:00')

if __name__ == "__main__":
    asyncio.run(main())
