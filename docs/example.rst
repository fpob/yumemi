Example
=======

Nearly all documentation in one example...

.. code-block:: python

    import yumemi

    client = yumemi.Client()

    # Check if API is OK.
    if not client.ping():
        print('AniDB is DOWN')

    # Login with your AniDB credentials.
    client.auth('my-username', 'my-password')

    # Optionally encrypt connection. Parameter is "UDP API key", you can find
    # that in Settings > Account.
    client.encrypt('udp-api-key')

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

And for ed2k utils...

.. code-block:: python

    import yumemi.ed2k

    ed2k_hash = yumemi.ed2k.file_ed2k('/tmp/foo')
    ed2k_link = yumemi.ed2k.file_ed2k_link('/tmp/foo')
