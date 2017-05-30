# Offspring

This is a collection of objects and patterns for working with processes in Python using the multiprocessing library.

The main idea is that you express your unit of work as a simple method on an object and then when that object is
instantiated the work will be run in a subprocess.


## Use cases

Offspring was built to address the following use cases for running code in a subprocess.


### Run something once

```python
from offspring import Subprocess


class MyTask(Subprocess):
    def __init__(self, arg1):
        # this is run in the parent process and is used to prepare your object
        self.arg = arg

    def run(self):
        # this will be run in the child process and completes your work
        # ...


MyTask('this is arg1').wait()
```


### Run in a loop

```python
from offspring import SubprocessLoop


class MyTask(SubprocessLoop):
    def __init__(self, arg1):
        # this is run in the parent process and is used to prepare your object
        self.arg = arg

    def begin(self):
        # called at the start of the loop in your child process

    def loop(self):
        # called each loop iteration in your your child process
        # it should return a sleep duration until the next loop, or False to stop the loop

    def end(self):
        # called at the end of the loop in your child process


MyTask('this is arg1').wait()
```


## Implementation details

### `.process`

Each `Subprocess` object has a `.process` attribute that is the `multiprocessing.Process` object.


### `.wait`

If you need to wait for your child process you can call `.wait` on your `Subprocess` object.


### `WAIT_FOR_CHILD`

If set to `True` on your `Subprocess` class then a `Pipe` will be used to block the parent process until the child has
started.  This is useful when you want to ensure that your `Subprocess` object is started and `.run` is called even if
the parent process exits quickly.

```python
class MyTask(Subprocess):
    WAIT_FOR_CHILD = True

    def run(self):
        print("This will always print")

MyTask().wait()
```

The `SubprocessLoop` class does this to ensure that your object has `begin` & `end` called (`loop` may not be called as
a TERM signal received during startup will prevent the loop from every actually completing other than `begin` & `end`).


### `TERMINATE_ON_SHUTDOWN`

If set to `False` then when `.shutdown` is called on a `Subprocess` object the child process **will not** be terminated
before being joined.  This means that the parent will block until the child completes the `.run` function.

```python
import time

class MyTask(Subprocess):
    TERMINATE_ON_SHUTDOWN = False

    def run(self):
        time.sleep(2)

# Note that we do not call .wait on the task here since we will automatically wait for the child
MyTask()
```
