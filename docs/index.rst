Welcome to Yumemi's documentation!
====================================

AniDB library for Python and simple CLI client. Also provides functions to
calculate ed2k hashes.

.. code-block:: python

    client = yumemi.Client()
    client.auth('login', '*****')

    response = client.call('ANIME', {'aid': 11829})
    # ...

    ed2k_hash = yumemi.ed2k.file_ed2k('/tmp/foo')
    # ...

.. note::

    This library not intends to wrap every single API message into function,
    method, or whatever. It just provides simple way to authenticate and then
    simplify sending commands in the correct form, respecting `flood protection
    policy <https://wiki.anidb.net/w/UDP_API_Definition#Flood_Protection>`_.


Installation
------------

Install it using pip ::

    pip3 install yumemi

or optionally with encrypt support ::

    pip3 install yumemi[encrypt]


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   cli
   example
   api
