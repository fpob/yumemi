API
===

AniDB UDP API is well documented at `AniDB Wiki`_.

.. _AniDB Wiki: https://wiki.anidb.net/w/UDP_API_Definition

AniDB
-----

.. automodule:: yumemi.anidb

.. autoclass:: yumemi.Socket
   :members:

.. autoclass:: yumemi.Response
   :members:

.. autoclass:: yumemi.Codec
   :members:

.. autoclass:: yumemi.EncryptCodec
   :members:

.. autoclass:: yumemi.Client
   :members:
   :special-members: __call__


Exceptions
^^^^^^^^^^

.. automodule:: yumemi.exceptions

.. autoclass:: yumemi.AnidbError

.. autoclass:: yumemi.SocketError

.. autoclass:: yumemi.SocketTimeout

.. autoclass:: yumemi.AnidbApiError
   :members:

.. autoclass:: yumemi.ServerError

.. autoclass:: yumemi.ClientError

.. autoclass:: yumemi.EncryptError


Ed2k
----

.. note::
   This mode is not imported with `yumemi` package.

.. autoclass:: yumemi.ed2k.Ed2k

.. autofunction:: yumemi.ed2k.file_ed2k

.. autofunction:: yumemi.ed2k.file_ed2k_link
