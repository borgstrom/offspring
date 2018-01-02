Offspring
=========

.. image:: https://img.shields.io/travis/borgstrom/offspring.svg
           :target: https://travis-ci.org/borgstrom/offspring

.. image:: https://img.shields.io/codecov/c/github/borgstrom/offspring.svg
           :target: https://codecov.io/github/borgstrom/offspring

.. image:: https://img.shields.io/pypi/v/offspring.svg
           :target: https://pypi.python.org/pypi/offspring
           :alt: Latest PyPI version


This is a collection of objects and patterns for working with processes in Python using the multiprocessing library.

The main idea is that you express your unit of work as a simple method on an object and then when that object is
instantiated the work will be run in a subprocess.


Use cases
---------

Offspring was built to address the following use cases for running code in a subprocess.


Run something once
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from offspring import Subprocess


    class MyTask(Subprocess):
        def init(self, arg1):
            # This is run in the parent process and is used to prepare your object.
            # It receives whatever arguments were supplied to the constructor.
            self.arg1 = arg1

        def run(self):
            # This will be run in the child process and completes your work.
            # ...


    MyTask('this is arg1').wait()


Run in a loop
~~~~~~~~~~~~~

.. code-block:: python

    from offspring import SubprocessLoop


    class MyTask(SubprocessLoop):
        def init(self, arg1):
            # This is the same as init for Subprocess.
            self.arg1 = arg1

        def begin(self):
            # Called before the start of the loop in your child process.
            # ...

        def loop(self):
            # Called each loop iteration in your your child process.
            # It can return a sleep duration until the next loop, or False to stop the loop.
            # ...

        def end(self):
            # Called after the end of the loop, before termination in your child process.
            # ...


    MyTask('this is arg1').wait()


Implementation details
----------------------

``.init(*args, **kwargs)``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Called when an instance of your class is created.  It receives the same arguments as the ``__init__`` method, so you are
encouraged to explicitly define the arguments you expect.


``.start()``
~~~~~~~~~~~~

Creates the subprocess.  This is automatically called unless you set ``EXPLICIT_START`` to ``True``.


``.wait()``
~~~~~~~~~~~

If you need to wait for your child process you can call ``.wait`` on your ``Subprocess`` object.  This is just a
shortcut to ``.join`` on the ``multiprocessing.Process`` object.


``.shutdown()``
~~~~~~~~~~~~~~~

This will send a ``TERM`` signal to the child process, unless ``TERMINATE_ON_SHUTDOWN`` is ``False``, and then calls
``.wait()`` to join the child process.  It is automatically called whenever the parent process exits via the ``atexit``
module.


``.process``
~~~~~~~~~~~~

Each ``Subprocess`` object has a ``.process`` attribute that is the ``multiprocessing.Process`` object.


``WAIT_FOR_CHILD``
~~~~~~~~~~~~~~~~~~

Defaults to ``False``.

If set to ``True`` on your ``Subprocess`` class then a ``Pipe`` will be used to block the parent process until the child
has started.  This is useful when you want to ensure that your ``Subprocess`` object is started and ``.run`` is called
even if the parent process exits quickly.

.. code-block:: python

    class MyTask(Subprocess):
        WAIT_FOR_CHILD = True

        def run(self):
            print("This will always print")

    MyTask()

The ``SubprocessLoop`` class does this to ensure that your object has ``begin`` & ``end`` called (``loop`` may not be
called as a TERM signal received during startup will prevent the loop from every actually completing other than
``begin`` & ``end``).


``TERMINATE_ON_SHUTDOWN``
~~~~~~~~~~~~~~~~~~~~~~~~~

Defaults to ``True``.

If set to ``False`` then when ``.shutdown`` is called on a ``Subprocess`` object the child process **will not** be
terminated before being joined.  This means that the parent will block until the child completes the ``.run`` function.

.. code-block:: python

    import time

    class MyTask(Subprocess):
        TERMINATE_ON_SHUTDOWN = False

        def run(self):
            time.sleep(2)

    MyTask()


``EXPLICIT_START``
~~~~~~~~~~~~~~~~~~

Defaults to ``False``.

If set to ``True`` then when you instantiate an object you must explicitly call ``.start()`` before the child process
will be spawned.

.. code-block:: python

    class MyTask(Subprocess):
        EXPLICIT_START = True

        def run(self):
            print("Running!")


    task = MyTask()
    # Do some other work
    task.start()
    # Running! is now printed
