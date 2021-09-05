API
===

Reference
---------

.. automodule:: yumemi
   :members:
   :undoc-members:
   :show-inheritance:


Example
-------

.. code-block:: python

    import yumemi

    # Your client name and version, create on https://anidb.net/software
    client = yumemi.Client('example', 1)

    # Check if API is OK
    if not client.ping():
        print('AniDB is DOWN')
        exit(1)

    # Optionaly encrypt connection
    client.encrypt('my-username', 'udp-api-key')

    # Login to AniDB
    client.auth('my-username', 'my-password')

    # Send some commands...
    result = client.command('ANIME', {'aid': 11829})
    if result.code == 230:
        aid = result.data[0][0]
        year = result.data[0][10]
        name = result.data[0][12]
        print(f'{name} (a{aid}) @ {year}')
    else:
        print(f'Error: {result.message}')

    # ... Send more commands...

    # And logout at the end
    client.logout()
