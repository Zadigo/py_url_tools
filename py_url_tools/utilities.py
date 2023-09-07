from kryptone.utils.file_readers import read_document
from kryptone.conf import settings
import random
from functools import lru_cache, wraps
from urllib.parse import (ParseResult, _coerce_args, quote, unquote_to_bytes,
                          urlparse)

from py_url_tools import PROJECT_PATH, constants


def string_to_unicode(text, encoding='utf-8', errors='strict'):
    if isinstance(text, bytes):
        return text.decode(encoding=encoding, errors=errors)
    return text


def unicode_to_string(text, encoding='utf-8', errors='strict'):
    if isinstance(text, bytes):
        return text.encode(encoding=encoding, errors=errors)
    return text


def convert_to_unicode(text, encoding='utf-8', errors='strict'):
    if not isinstance(text, (bytes, str)):
        raise

    if isinstance(text, str):
        return text
    return text.decode(encoding=encoding, errors=errors)


def convert_to_bytes(text, encoding='utf-8', errors='strict'):
    if isinstance(text, bytes):
        return text
    return text.encode(encoding=encoding, errors=errors)


def url_strip(value):
    result = value.strip(constants.C0_CONTROL_OR_SPACE)
    return result.translate(constants.ASCII_TAB_OR_NEWLINE_TRANSLATION_TABLE)


class SafeParser:
    def __init__(self, value, encoding='utf8', path_encoding='utf8'):
        if not isinstance(value, ParseResult):
            value = urlparse(value)

        try:
            netloc = value.netloc.encode('idna').decode()
        except UnicodeError:
            netloc = value.netloc

        path_safe_characters = constants.PATH_SAFE_CHARACTERS
        self.url_parts = (
            value.scheme,
            netloc,
            quote(value.path.encode(path_encoding), path_safe_characters),
            quote(value.params.encode(path_encoding), path_safe_characters),
            quote(value.query.encode(encoding), path_safe_characters),
            quote(value.fragment.encode(encoding), path_safe_characters)
        )

    @property
    def get_url_parts(self):
        return self.url_parts


def unquote_path(path):
    """The standard library `unquote()` does not work for non-UTF-8
    percent-escaped characters, they get lost. 
    e.g., '%a3' becomes 'REPLACEMENT CHARACTER' (U+FFFD)"""
    for item in ('2f', '2F', '3f', '3F'):
        path = path.replace('%' + item, '%25' + item.upper())
    return unquote_to_bytes(path)


def parse_qsl_to_bytes(qs, keep_blank_values=False):
    """Works as `parse_qsl` but return the values as bytes

    >>> url = 'http://www.example.org/something/here?google=1&a=2'
    ... result = parse_qsl_to_bytes(url)
    ... [(b'google', b'1'), (b'a', b'2')]
    """
    qs, coerced_result = _coerce_args(qs)
    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    # print(pairs)

    final_result = []
    for pair in pairs:
        if not pair:
            continue

        items = pair.split('=', 1)
        if len(items) != 2:
            if keep_blank_values:
                items.append('')
            else:
                continue

        if len(items[1]) or keep_blank_values:
            name = items[0].replace('+', ' ')
            name = unquote_to_bytes(name)
            name = coerced_result(name)
            value = items[1].replace('+', ' ')
            value = unquote_to_bytes(value)
            value = coerced_result(value)
            final_result.append((name, value))
    return final_result


def lazy(func, *items):
    pass


def keep_lazy(*items):
    if not items:
        raise ValueError

    def decorator(func):
        # lazy_function = lazy(func, *items)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # return lazy_function(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def lazy_text(func):
    return keep_lazy(str)(func)


# def test_function():
#     return 'google'


# print(lazy_text(test_function))

# from django.utils.safestring import mark_safe

# def syncer(text):
#     return text + 'want'


# @lazy_text(syncer)
# def simple_unicode_to_string(text):
#     return text


# print(simple_unicode_to_string('something'))


def drop_null(items, remove_empty_strings=True):
    for item in items:
        if remove_empty_strings and item == '':
            continue

        if item is not None:
            yield item


def keep_while(predicate, items):
    for item in items:
        if not predicate(item):
            continue
        yield item


def drop_while(predicate, items):
    for item in items:
        if predicate(item):
            continue
        yield item


def tokenize(func):
    @lru_cache(maxsize=100)
    def reader(filename, *, as_list=False):
        data = func(filename)
        return data.split('\n') if as_list else data
    return reader


@tokenize
def read_document(filename):
    """Reads a document of some sort"""
    path = PROJECT_PATH / 'data'
    with open(path, mode='r', encoding='utf-8') as f:
        data = f.read()
    return data


def random_user_agent(func):
    def wrapper():
        data = func(
            PROJECT_PATH / 'data/user_agents.txt'
        )
        user_agents = data.split('\n')
        return random.choice(user_agents)
    return wrapper


RANDOM_USER_AGENT = random_user_agent(read_document)
