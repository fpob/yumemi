import sys
from ctypes.util import find_library


_LIBNAME = find_library('rhash')

if not _LIBNAME:
    if sys.platform == "win32":
        _LIBNAME = "librhash.dll"
    elif sys.platform == "darwin":
        _LIBNAME = "librhash.1.dylib"
    elif sys.platform == "cygwin":
        _LIBNAME = "cygrhash.dll"
    elif sys.platform == "msys":
        _LIBNAME = "msys-rhash.dll"
    else:
        _LIBNAME = "librhash.so.1"
