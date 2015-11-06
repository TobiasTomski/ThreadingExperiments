import threading
import time
import os
import Queue as queue

q = queue.Queue()

q.put(False)

class counter(object):
    def __init__(self):

        wait_label = "Loading"

        self.stop_flag = q.get()

        while not self.stop_flag:
            try:
                self.stop_flag = q.get_nowait()
            except:
                pass
            os.system('clear') # might need to change this command for linux
            wait_label += "."
            print(wait_label)
            time.sleep(1)

class other(counter):
    def __init__(self):

        time.sleep(15)

        q.put(True)

counter_thread = threading.Thread(None, counter)
counter_thread.start()

other_thread = threading.Thread(None, other)
other_thread.start()
