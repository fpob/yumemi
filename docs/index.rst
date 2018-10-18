Welcome to Yumemi's documentation!
====================================

AniDB library for Python and simple CLI client. Also provides functions to
calculate ed2k hash.

.. code-block:: python

    client = yumemi.Client()
    client.auth('login', '*****')
    
    response = client.call('ANIME', {'aid': 11829})
    # ...

.. note::

    This library not intends to wrap every single API message into function,
    method, or whatever. It just provides simple way to authenticate and then
    simplify sending commands in the correct form, respecting flood protection
    policy.


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


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   cli
   example
   api
