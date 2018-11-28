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
   :show-inheritance:

.. autoclass:: yumemi.SocketError
   :show-inheritance:

.. autoclass:: yumemi.SocketTimeout
   :show-inheritance:

.. autoclass:: yumemi.AnidbApiError
   :show-inheritance:
   :members:

.. autoclass:: yumemi.ServerError
   :show-inheritance:

.. autoclass:: yumemi.ClientError
   :show-inheritance:

.. autoclass:: yumemi.EncryptError
   :show-inheritance:


Ed2k
----

.. automodule:: yumemi.ed2k

.. note::
   This module is not automatically imported with `yumemi`.

.. autoclass:: yumemi.ed2k.Ed2k

.. autofunction:: yumemi.ed2k.file_ed2k

.. autofunction:: yumemi.ed2k.file_ed2k_link
