import multiprocessing
import os
import time

try:
    from Queue import Empty
except ImportError:
    from queue import Empty

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


def test_wait_for_child():
    class MyProcess(Subprocess):
        WAIT_FOR_CHILD = True

        def run(self):
            time.sleep(0.25)

    proc = MyProcess()
    assert proc.process.is_alive()
    proc.wait()
    assert not proc.process.is_alive()


def test_terminate_on_shutdown():
    class MyProcess(Subprocess):
        TERMINATE_ON_SHUTDOWN = False

        def run(self):
            time.sleep(0.5)

    proc = MyProcess()
    start = time.time()
    proc.shutdown()
    assert time.time() - start >= 0.5


def test_explicit_start():
    class MyProcess(Subprocess):
        EXPLICIT_START = True

        def run(self):
            time.sleep(0.1)

    proc = MyProcess()
    assert proc.process is None
    proc.start()
    assert proc.process is not None
    proc.shutdown()


def test_start_assertion():
    class MyProcess(Subprocess):
        def run(self):
            time.sleep(0.1)

    proc = MyProcess()
    with pytest.raises(AssertionError):
        proc.start()
    proc.shutdown()


def test_atexit():
    class MyProcess(Subprocess):
        WAIT_FOR_CHILD = True

        def run(self):
            time.sleep(0.5)

    proc = MyProcess()
    assert proc.process.is_alive()

    # we can't really simulate atexit (and we trust that the python tests ensure atexit works)
    # so we just call our class method directly and ensure it shuts down our process
    Subprocess.atexit()

    assert not proc.process.is_alive()


def test_loop():
    class MyLoop(SubprocessLoop):
        def init(self, q):
            self.counter = 0
            self.q = q

        def loop(self):
            self.counter += 1
            self.q.put_nowait(self.counter)
            if self.counter > 3:
                return False
            return 0.1 * self.counter

    q = multiprocessing.Queue()
    MyLoop(q)
    assert(q.get()) == 1

    with pytest.raises(Empty):
        q.get(block=True, timeout=0.05)

    assert(q.get()) == 2

    with pytest.raises(Empty):
        q.get(block=True, timeout=0.1)

    assert(q.get()) == 3

    with pytest.raises(Empty):
        q.get(block=True, timeout=0.2)

    assert(q.get()) == 4


def test_loop_sigterm():
    class MyLoop(SubprocessLoop):
        def init(self, q):
            self.counter = 0
            self.q = q

        def loop(self):
            self.counter += 1
            self.q.put_nowait(self.counter)
            return 0.1

    # start the loop and give it 150ms, which should produce two items on the queue
    q = multiprocessing.Queue()
    loop = MyLoop(q)
    time.sleep(0.15)
    os.kill(loop.process.pid, 15)
    assert(q.get()) == 1
    assert(q.get()) == 2

    # after that the queue should be empty
    with pytest.raises(Empty):
        q.get(block=True, timeout=0.01)

    # sleep for a bit and make sure nothing else ends up in the queue
    time.sleep(0.25)
    with pytest.raises(Empty):
        q.get(block=True, timeout=0.01)

    assert not loop.process.is_alive()
