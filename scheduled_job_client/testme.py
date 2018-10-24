# test me
import time
import random
import sys


def test_me(count=10, span=10):
    count = int(count)
    chunk = int(round(100/count))
    progress = 1
    for i in range(0, count):
        progress = random.randint(i * chunk, (i + 1) * chunk)
        print('{}'.format(progress))
        sys.stdout.flush()
        time.sleep(int(span))
    print('fini')
