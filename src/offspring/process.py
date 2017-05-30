import atexit
import logging
import multiprocessing
import signal
import sys
import time

log = logging.getLogger(__name__)


class Subprocess(object):
    """Object process implementation.

    The __init__() method runs in the parent process and sets up the instance however you need before a copy is made for
    the subprocess.

    The run() method runs in the child process and implements whatever logic this process should execute.
    """
    _INSTANCES = None

    WAIT_FOR_CHILD = False
    TERMINATE_ON_SHUTDOWN = True

    def __new__(cls, *args, **kwargs):
        obj = super(Subprocess, cls).__new__(cls)
        obj.process = None

        try:
            cls._INSTANCES.append(obj)
        except AttributeError:
            cls._INSTANCES = [obj]

        return obj

    def __init__(self):
        self.start()

    def start(self):
        if self.WAIT_FOR_CHILD:
            # we use a pipe to confirm that the child has started up before we move on
            def bootstrap(writer):
                writer.send(True)
                self.run()

            startup_reader, startup_writer = multiprocessing.Pipe(duplex=False)
            self.process = multiprocessing.Process(target=bootstrap, args=(startup_writer,))
            self.process.start()

            try:
                startup_reader.recv()
            except EOFError:
                log.error("Failed to start subprocess for %s", self)
                raise
        else:
            self.process = multiprocessing.Process(target=self.run)
            self.process.start()

    @classmethod
    def atexit(cls):
        """Called when the process that imported this module exits to cleanup all child processes"""
        def recursively_shutdown(cls):
            for klass in cls.__subclasses__():
                recursively_shutdown(klass)
                try:
                    for obj in klass._INSTANCES:
                        obj.shutdown()
                except TypeError:
                    # _INSTANCES is not a list, no processes were created on this class
                    pass
        recursively_shutdown(cls)

        # join all child processes
        multiprocessing.active_children()

    def shutdown(self):
        if self.process:
            log.debug("Shutting down %s", self)
            if self.TERMINATE_ON_SHUTDOWN:
                self.process.terminate()
            self.process.join()

    def run(self):
        raise NotImplementedError

    def wait(self):
        self.process.join()


atexit.register(Subprocess.atexit)


class SubprocessLoop(Subprocess):
    """Run a loop based subprocess

    The begin() method is called before the loop begins.

    The loop() method implements the main logic, returns how long to sleep before the next loop or False to stop the
    loop.

    The end() is called when it ends, regardless of how it ends.
    """
    WAIT_FOR_CHILD = True

    def signal_handler(self, signum, frame):
        """Handle signals within our child process to terminate the main loop"""
        log.info("Caught signal %s", signum)
        self.alive = False

    def run(self):
        signal.signal(signal.SIGTERM, self.signal_handler)
        self.alive = True

        try:
            self.begin()
            while self.alive:
                loop_status = self.loop()
                if loop_status is False:
                    self.alive = False
                else:
                    time.sleep(loop_status or 0.05)
        except (SystemExit, KeyboardInterrupt):
            log.debug("Exit via interrupt")
        finally:
            self.end()
            sys.exit()

    def begin(self):
        pass

    def loop(self):
        raise NotImplementedError

    def end(self):
        pass
