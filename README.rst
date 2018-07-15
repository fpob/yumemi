Yumemi
======

AniDB library for Python and simple CLI client. Also provides functions to
calculate ed2k hash.

.. code:: python

    client = yumemi.Client()
    client.auth('login', '*****')
    
    response = client.call('ANIME', {'aid': 11829})
    # ...


CLI
---

Command line client can only test connection to the API server and add files to
mylist. Thats all, nothing else will be added, i think. ::

    Usage: yumemi [OPTIONS] [FILES]...
     
       AniDB client for adding files to mylist.
     
    Options:
      --version             Show the version and exit.
      --ping                Test connection to AniDB API server.
      -u, --username TEXT
      -p, --password TEXT
      --encrypt TEXT        Ecrypt messages. Parameter value is API Key.
      -w, --watched         Mark files as watched.
      -W, --view-date DATE  Set viewdate to certain date. Implies -w/--watched.
                            Formats: Y-m-d[ H:M[:S]] | y H:M (yesterday) | -#[d]
                            H:M (before # days).
      -d, --deleted         Set file state to deleted.
      -e, --edit            Set edit flag to true.
      -j, --jobs TEXT       Number of adding processes. Default is CPU count.
      -h, --help            Show this message and exit.

Values of options ``username``, ``encrypt`` and ``jobs`` are also read from
environment variables prefixed with ``YUMEMI_``. For example if you don't want
to write username every time you adding files, type following line into
terminal or place it to your ``~/.profile`` file ::

    export YUMEMI_USERNAME=your-username

Ed2k
****

Simple CLI is also in the Ed2k module. You can generate Ed2k links by executing
``yumemi.ed2k`` module. ::

    python3 -m yumemi.ed2k [FILE...]


Installation
------------

Install it using pip ::

    pip3 install yumemi

or clone repository ::

    git clone https://github.com/fpob/yumemi
    cd yumemi

and install Python package including dependencies ::

    python3 setup.py install

To use optional encryption, package ``pycrypto`` must be installed ::

    pip3 install pycrypto


Documentation
-------------

Module API is not so complex, you can easily use ``pydoc yumemi.Client`` and
``pydoc yumemi.Response``.

AniDB API is well documented on `AniDB Wiki`_.

.. note::

    This library not intends to wrap every single API message into function,
    method, or whatever. It just provides simple way to authenticate and then
    simplify sending commands in the correct form, respecting flood protection
    policy.

.. _AniDB Wiki: https://wiki.anidb.net/w/UDP_API_Definition

Example
*******

.. code:: python

    import yumemi

    client = yumemi.Client()

    # Login with your AniDB credentials.
    client.auth('my-username', 'my-password')

    # Optionally encrypt connection. Parameter is "UDP API key", you can find
    # that in Settings > Account.
    client.encrypt('udp-api-key')

    # Check if API is OK.
    if not client.ping():
        print('AniDB is DOWN')

    # Send some commands...
    response = client.call('ANIME', {'aid': 11829})
    if response.code == 230:
        aid = response.data[0][0]
        year = response.data[0][10]
        name = response.data[0][12]
    else:
        print(response.message)
    # ...

    # And logout.
    client.logout()

    # Check if you are logged in.
    if client.is_logged_in():
        print('Still logged in...')

.. code:: python

    import yumemi.ed2k

    ed2k_hash = yumemi.ed2k.file_ed2k('/tmp/foo')
    ed2k_link = yumemi.ed2k.file_ed2k_link('/tmp/foo')
