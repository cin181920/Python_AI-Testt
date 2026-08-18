import datetime
import logging
import asyncio
from typing import Dict, Any, List
from abc import ABC, abstractmethod

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# 1. User management & quota control module
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
# 2. Action Strategies (Optional Extension - OOP Design)
# ---------------------------------------------------------
class ActionStrategy(ABC):
    @abstractmethod
    async def execute(self, target: str, **kwargs):
        pass

class SyncAction(ActionStrategy):
    async def execute(self, target: str, **kwargs):
        logger.info(f"Performing SYNC on {target} with params: {kwargs}")
        await asyncio.sleep(0.1) # Simulasi proses IO/jaringan

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
# 3. Task data model
# ---------------------------------------------------------
class Task:
    def __init__(self, user: str, time: str, action: str, target: str, params: Dict[str, Any] = None):
        self.user = user
        self.time = time
        self.action = action
        self.target = target
        # Task parameter bisa dikonfigurasi via dictionary input
        self.params = params or {} 

# ---------------------------------------------------------
# 4. Task executor (Extensible)
# ---------------------------------------------------------
class TaskExecutor:
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

    async def execute_task(self, task: Task):
        user = self.user_manager.get_user(task.user)
        if not user:
            logger.error(f"User {task.user} not found.")
            return

        if not user.can_execute():
            logger.warning(f"User {user.username} has exceeded quota. Task {task.action} on {task.target} aborted.")
            return

        # Potong kuota di awal untuk mencegah "Race Condition" pada eksekusi asinkron
        user.increment_executed()

        strategy = ActionFactory.get_strategy(task.action)
        if not strategy:
            logger.error(f"Action {task.action} is not supported.")
            user.executed -= 1 # Rollback kuota
            return
            
        logger.info(f"Executing {task.action} on {task.target} for {user.username}")
        try:
            await strategy.execute(task.target, **task.params)
        except Exception as e:
            logger.error(f"Task {task.action} failed: {e}")
            # Opsional: Kembalikan kuota jika eksekusi error
            # user.executed -= 1

# ---------------------------------------------------------
# 5. Scheduling system
# ---------------------------------------------------------
class Scheduler:
    def __init__(self, executor: TaskExecutor):
        self.tasks: List[Task] = []
        self.executor = executor

    def add_task(self, task: Task):
        self.tasks.append(task)

    async def run(self, current_time_override: str = None):
        now = current_time_override or datetime.datetime.now().strftime('%H:%M')
        logger.info(f"Scheduler checking tasks for time: {now}")
        
        # Ambil semua task pada waktu ini
        tasks_to_run = [task for task in self.tasks if task.time == now]
        
        if not tasks_to_run:
            logger.info("No tasks to run at this time.")
            return
            
        # Eksekusi secara asinkron agar satu user bisa menjalankan banyak task sekaligus
        coroutines = [self.executor.execute_task(task) for task in tasks_to_run]
        await asyncio.gather(*coroutines)

# ---------------------------------------------------------
# Simulasi Main Program
# ---------------------------------------------------------
async def main():
    # Setup
    user_manager = UserManager()
    user_manager.add_user('alice', 3)
    user_manager.add_user('bob', 5)

    executor = TaskExecutor(user_manager)
    scheduler = Scheduler(executor)

    # Menambahkan Tasks (dengan parameter dictionary)
    scheduler.add_task(Task('alice', '12:00', 'sync', '/data/x', {'mode': 'fast'}))
    scheduler.add_task(Task('bob', '12:00', 'backup', '/srv/y', {'compression': 'gzip'}))
    scheduler.add_task(Task('alice', '12:00', 'delete', '/tmp/z', {'force': True}))
    
    # Task ekstra untuk mendemonstrasikan pembatasan kuota (Alice hanya punya 3 kuota)
    scheduler.add_task(Task('alice', '12:00', 'sync', '/data/w'))
    scheduler.add_task(Task('alice', '12:00', 'sync', '/data/v')) # Ini akan ditolak

    # Jalankan Scheduler (Simulasi waktu jam 12:00)
    await scheduler.run(current_time_override='12:00')

if __name__ == "__main__":
    asyncio.run(main())
