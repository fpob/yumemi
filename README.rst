Yumemi
======

AniDB library for Python and simple CLI client. Also provides functions to
calculate ed2k hashes.

.. code:: python

    client = yumemi.Client()
    client.auth('login', '*****')

    response = client.call('ANIME', {'aid': 11829})
    # ...

    ed2k_hash = yumemi.ed2k.file_ed2k('/tmp/foo')
    # ...


CLI
---

Command line client can only test connection to the API server and add files to
mylist. Thats all, nothing else will be added, i think. ::

   Usage: yumemi [OPTIONS] FILES...

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
     -j, --jobs INTEGER    Number of adding processes. Default is CPU count.
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

    python3 -m yumemi.ed2k [FILES...]


Installation
------------

Install it using pip ::

    pip3 install yumemi

or optionally with encrypt support ::

    pip3 install yumemi[encrypt]


Documentation
-------------

Documentation can be found at `Read The Docs`_.

.. _Read The Docs: https://yumemi.readthedocs.io/
