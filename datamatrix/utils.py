import logging
logger = logging.getLogger('datamatrix')


def safe_decode(s, enc='utf-8', errors='strict'):
    """Takes any object and returns it as a str."""
    if isinstance(s, str):
        return s
    if isinstance(s, bytes):
        return s.decode(enc, errors)
    # Numeric values are encoded right away
    try:
        assert(int(s) == float(s))
        return str(int(s))
    except Exception:
        try:
            return str(float(s))
        except Exception:
            pass
    # Some types need to be converted to unicode, but require the encoding
    # and errors parameters. Notable examples are Exceptions, which have
    # strange characters under some locales, such as French. It even appears
    # that, at least in some cases, they have to be encodeed to str first.
    # Presumably, there is a better way to do this, but for now this at
    # least gives sensible results.
    if isinstance(s, Exception):
        try:
            return safe_decode(bytes(s), enc=enc, errors=errors)
        except Exception:
            pass
    # For other types, the unicode representation doesn't require a specific
    # encoding. This mostly applies to non-stringy things, such as integers.
    return str(s)


def safe_encode(s, enc='utf-8', errors='strict'):
    """Takes any object and returns it as a bytes."""
    if isinstance(s, bytes):
        return s
    # Numeric values are encoded right away
    try:
        assert(int(s) == float(s))
        return str(int(s)).encode()
    except Exception:
        try:
            return str(float(s)).encode()
        except Exception:
            pass
    if hasattr(s, u'encode'):
        return s.encode(enc, errors)
    return bytes(s)
