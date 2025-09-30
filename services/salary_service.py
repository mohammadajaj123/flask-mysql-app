from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from extensions import db
from models.user import User
from services.transaction_service import TransactionService
import atexit

class SalaryService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.salary_amount = 5000  
        self.daily_salary = self.salary_amount / 30  
    
    def start(self):
        """Start the salary scheduler"""
        self.scheduler.add_job(
            func=self.distribute_salaries,
            trigger='interval',
            days=1,
            next_run_time=datetime.now() + timedelta(seconds=10)
        )
        self.scheduler.start()
        atexit.register(lambda: self.scheduler.shutdown())
    
    def distribute_salaries(self):
        """Distribute daily salary to all users"""
        print("Distributing daily salaries...")
        users = User.query.all()
        
        for user in users:
            try:
                TransactionService.create_transaction(
                    user.id, self.daily_salary, 'credit', 'salary',
                    'Daily Salary', 'Automatic daily salary distribution'
                )
                print(f"Salary distributed to {user.name}: {self.daily_salary} ILS")
            except Exception as e:
                print(f"Failed to distribute salary to {user.name}: {e}")
    
    def manual_salary(self, user_id, amount):
        """Admin can manually add salary"""
        return TransactionService.create_transaction(
            user_id, amount, 'credit', 'salary',
            'Manual Salary', 'Admin manual salary distribution'
        )

salary_service = SalaryService()