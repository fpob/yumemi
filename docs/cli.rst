CLI
===

.. click:: yumemi.cli:main
   :prog: yumemi
   :nested: full


Rename Format
-------------

Rename format is template string which support ``$``-based substitions:

- ``$$`` is an escape; it is replaced with a single $.
- ``$identifier`` and ``${identifier}`` names a substitution placeholder
  matching a key of "identifier"

Example: ::

   $aname - $epno - $epname - [$gsname]($crc32)

List of all variables in the template string:

.. autodata:: yumemi.cli.FILE_KEYS
