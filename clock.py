from apscheduler.schedulers.blocking import BlockingScheduler
import os

# Get Command info
runCmd = "python bitbank_bot.py " + "XRP/JPY"

# Start the scheduler
sched = BlockingScheduler()

# Schedules job_function to be run on the 1 day of months at 09:00

@sched.scheduled_job('cron', day='1', hour='0', minute='0')

def timed_job():

    os.system(runCmd)

sched.start()