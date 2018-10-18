# test me
import time
import random


def test_me():
    for i in range(0, 10):
        print('{}'.format((i * 10) + random.randint(1, 10)))
        time.sleep(10)
