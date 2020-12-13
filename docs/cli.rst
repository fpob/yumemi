CLI
===

Add files to mylist
-------------------

With library is also installed simple script to add files to mylist ::

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
----

Ed2k module has also very simple CLI which takes list of files and prints ed2k
liks

.. code-block:: none

    python3 -m yumemi.ed2k [FILE...]
