# myapp/tasks.py
import time



def my_background_task(n):
    time.sleep(n)
    return f"Task completed after {n} seconds"