from apscheduler.schedulers.background import BackgroundScheduler
from app.notification import generate_daily_notifications
import logging

scheduler = BackgroundScheduler()

def start_scheduler():
    # Run the job every hour (or set to 'interval', minutes=1 for testing)
    # For testing purposes, we will run it every 5 minutes.
    scheduler.add_job(generate_daily_notifications, 'interval', minutes=5)
    scheduler.start()
    logging.info("Background scheduler started.")