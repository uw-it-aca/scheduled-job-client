# test me
import time
import random
import sys


def test_me():
    for i in range(0, 10):
        print('{}'.format((i * 10) + random.randint(1, 10)))
        sys.stdout.flush()
        time.sleep(10)
