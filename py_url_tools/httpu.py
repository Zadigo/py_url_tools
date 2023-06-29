from base64 import b64encode
from typing import Any, MutableMapping
from py_url_tools import utilities


class Header(MutableMapping):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if not isinstance(value, list):
                value = [value]
            setattr(self, key, value)

    def __str__(self):
        return str(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]

    def __setitem__(self, key, value):
        if not isinstance(value, list):
            value = [value]

        items = getattr(self, key, [])
        if items:
            items.extend(value)
            value = items
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key, None)

    def __iter__(self):
        return iter(self.__dict__.items())

    def __len__(self):
        return len(self.__dict__)

    def clean(self, value):
        return value.strip()


def header_to_dictionnary(byte_text):
    """
    Convert 
    >>> header = b"Content-type: text/html\\n\\rAccept: gzip\\n\\n"
    ... result = header_to_dictionnary(header)
    ... {'Content-type': ['text/html'], 'Accept': ['gzip']}
    """
    items = byte_text.splitlines()
    headers_tuples = [item.split(b":", 1) for item in items]
    # print(headers_tuples)
    header_instance = Header()
    for item in headers_tuples:
        if len(item) != 2:
            continue

        key, value = item
        header_instance[key.strip()] = value.strip()
    return header_instance


def basic_authentication_header(username, password, encoding='ISO-8859-1'):
    username = utilities.string_to_unicode(username)
    password = utilities.string_to_unicode(password)
    authentication = f'{username}:{password}'
    encoded_authentication = b64encode(
        utilities.convert_to_bytes(authentication, encoding=encoding)
    )
    return b64encode(encoded_authentication)

# h = header_to_dictionnary(b"Content-type: text/html\n\rAccept: gzip\n\n")
# print(h)
# h = Header(key='kendall')
# h.update(key='name')
# print(h)
