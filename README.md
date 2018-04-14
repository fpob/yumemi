# Yumemi

AniDB library for Python and simple CLI client.

*This library not intends to wrap every single API message into function,
method, or whatever. It just provides simple way to authenticate and then
simplify sending commands in correct form respecting flood protection.*


```python
client = yumemi.Client()
client.auth('login', '*****')

response = client.call('ANIME', {'aid': 11829})
# ...
```

## CLI

Command line client can only test connection to the API server and add files to
mylist. Thats all, nothing else will be added, i think.

```
Usage: yumemi [OPTIONS] [FILES]...

  AniDB client for adding files to mylist.

Options:
  --ping                Test connection to AniDB API server.
  -u, --username TEXT
  -p, --password TEXT
  -w, --watched         Mark files as watched.
  -W, --view-date DATE  Set viewdate to certain date. Implies -w/--watched.
                        Formats: Y-m-d[ H:M[:S]] | y H:M (yesterday) | -#[d]
                        H:M (before # days).
  -d, --deleted         Set file state to deleted.
  -e, --edit            Set edit flag to true.
  -j, --jobs TEXT       Number of adding processes. Default is CPU count.
  -h, --help            Show this message and exit.
```

## Installation

Clone repository

```
git clone https://github.com/fpob/yumemi
cd yumemi
```

and install Python package including dependencies

```
python3 setup.py install
```

To use optional encryption, package `pycrypto` must be installed

```
pip3 install pycrypto
```
