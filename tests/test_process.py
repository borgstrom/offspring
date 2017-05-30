import multiprocessing
import Queue
import time

import pytest

from offspring.process import Subprocess, SubprocessLoop


def test_subprocess_basic():
    class MyProcess(Subprocess):
        def run(self):
            time.sleep(0.25)

    proc = MyProcess()
    time.sleep(0.2)
    assert proc.process.is_alive()
    proc.wait()
    assert not proc.process.is_alive()


def test_wait_for_child_start():
    class MyProcess(Subprocess):
        WAIT_FOR_CHILD = True

        def run(self):
            time.sleep(0.25)

    proc = MyProcess()
    assert proc.process.is_alive()
    proc.wait()
    assert not proc.process.is_alive()


def test_loop():
    class MyLoop(SubprocessLoop):
        def __init__(self, q):
            self.counter = 0
            self.q = q
            self.start()

        def loop(self):
            self.counter += 1
            self.q.put(self.counter)
            if self.counter > 3:
                return False
            return 0.1 * self.counter

    q = multiprocessing.Queue()
    loop = MyLoop(q)
    assert(q.get()) == 1

    with pytest.raises(Queue.Empty):
        q.get(block=True, timeout=0.05)

    assert(q.get()) == 2

    with pytest.raises(Queue.Empty):
        q.get(block=True, timeout=0.1)

    assert(q.get()) == 3

    with pytest.raises(Queue.Empty):
        q.get(block=True, timeout=0.2)

    assert(q.get()) == 4
