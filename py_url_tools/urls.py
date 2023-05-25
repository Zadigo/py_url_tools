import dataclasses
import os
import posixpath
from urllib.parse import (parse_qs, parse_qsl, quote, unquote, urldefrag,
                          urlencode, urlparse, urlsplit, urlunparse,
                          urlunsplit)
from urllib.request import pathname2url, url2pathname

from py_url_tools import constants, utilities


def safe_url_string(url, encoding='utf-8', path_encoding='utf-8', quote_path=True):
    decoded_url = utilities.convert_to_unicode(
        url,
        encoding=encoding,
        errors='percentcode'
    )
    url_parts = urlsplit(utilities.url_strip(decoded_url))

    netloc_bytes = b''
    if url_parts.username is not None:
        safe_username = quote(
            unquote(url_parts.username),
            constants.USERINFO_SAFEST_CHARACTERS
        )
        netloc_bytes = netloc_bytes + safe_username.encode(encoding)

    if url_parts.username is not None:
        safe_password = quote(
            unquote(url_parts.password),
            constants.USERINFO_SAFEST_CHARACTERS
        )
        netloc_bytes = netloc_bytes + safe_password.encode(encoding)
        netloc_bytes = netloc_bytes + b"@"

    if url_parts.hostname is not None:
        try:
            netloc_bytes += url_parts.hostname.encode('idna')
        except UnicodeError:
            # IDNA encoding can fail for too long labels (>63 characters) or
            # missing labels (e.g. http://.example.com)
            netloc_bytes += url_parts.hostname.encode(encoding)

    if url_parts.port is not None:
        netloc_bytes += b":"
        netloc_bytes += str(url_parts.port).encode(encoding)

    netloc = netloc_bytes.decode()

    if quote_path:
        path = quote(
            url_parts.path.encode(path_encoding),
            constants.PATH_SAFEST_CHARACTERS
        )
    else:
        path = url_parts.path

    if url_parts.scheme in constants.SPECIAL_SCHEMES:
        query = quote(
            url_parts.query.encode(encoding),
            constants.SPECIAL_QUERY_SAFEST_CHARACTERS
        )
    else:
        query = quote(
            url_parts.query.encode(encoding),
            constants.SPECIAL_QUERY_SAFEST_CHARACTERS
        )

    return urlunsplit(
        (
            url_parts.scheme,
            netloc,
            path,
            query,
            quote(
                url_parts.fragment.encode(encoding),
                constants.FRAGMENT_SAFEST_CHARS
            )
        )
    )


def safe_download_url(url, encoding='utf-8', path_encoding='utf-8'):
    safe_url = safe_url_string(
        url,
        encoding=encoding,
        path_encoding=path_encoding
    )
    url_object = urlsplit(safe_url)
    if url_object.path:
        path = constants.PARENT_DIRECTORIES.sub(
            '', posixpath.normpath(url_object.path))
        if safe_url.endswith('/') and not path.endswith('/'):
            path = path + '/'
        else:
            path = '/'
    return urlunsplit(
        (
            url_object.scheme,
            url_object.netloc,
            url_object.path,
            url_object.query,
            ''
        )
    )


def is_url(value):
    scheme = value.partition('://')[0]
    return scheme in ('file', 'http', 'https')


def get_url_parameter(url, name, default=None, keep_blank_values=False):
    url_object = urlsplit(str(url))
    query = parse_qs(
        url_object[3],
        keep_blank_values=keep_blank_values
    )
    if name in query:
        return query[name][0]
    return default


@dataclasses.dataclass
class URLParameter:
    key: str
    value: str

    def join(self):
        return f'{self.key}={self.value}'

    def replace(self, value):
        self.value = value

    def deconstruct(self):
        return (self.key, self.value)


def clean_url_query_parameters(url, names=[], separator='&', key_value_separator='=', unique=True, keep_fragments=False):
    if not isinstance(names, (tuple, list)):
        raise

    url, fragment = urldefrag(url)
    url = str(url)
    fragment = str(fragment)

    parameter_objects = []

    base, _, query = url.partition('?')
    tokens = query.split(separator)
    for token in tokens:
        if not token:
            continue

        key, value = token.split(key_value_separator)
        parameter_objects.append(URLParameter(key, value))

    seen_keys = set()
    result_list = []
    for item in parameter_objects:
        if unique:
            if item.key in seen_keys:
                continue

        if names:
            if item.key not in names:
                continue

        result_list.append(item)
        seen_keys.add(item.key)

    params = [item.join() for item in result_list]
    joined_params = f'{separator}'.join(params)
    url = f'?{joined_params}'

    if keep_fragments and fragment:
        url = url + f'#{fragment}'

    return base + url


def add_or_replace_parameter(url, params={}):
    url_object = urlsplit(url)
    current_params = parse_qsl(
        url_object.query,
        keep_blank_values=True
    )
    new_params = []
    seen_keys = set()

    for param in current_params:
        name, value = param

        if name in seen_keys:
            continue

        if name in params:
            new_params.append(URLParameter(name, params[name]))
        elif name not in params:
            new_params.append(URLParameter(name, value))
        seen_keys.add(name)

    for key in params.keys():
        if key not in seen_keys:
            new_params.append(URLParameter(key, params[key]))

    items = map(lambda x: x.deconstruct(), new_params)
    query = urlencode(list(items))
    return urlunsplit(url_object._replace(query=query))


def path_to_file_uri(path):
    result = pathname2url(os.path.abspath(path))
    return f"file:///{result.lstrip('/')}"


def file_uri_to_path(url):
    url_path = urlparse(url).path
    return url2pathname(url_path)


def convert_to_uri(url):
    drive = os.path.splitdrive(url)
    if drive:
        return path_to_file_uri(url)
    url_object = urlparse(url)
    return url_object if url_object.scheme else path_to_file_uri(url)


def clean_url(url, keep_blank_values=True, keep_fragments=False, encoding='utf-8'):
    if isinstance(url, str):
        url = utilities.url_strip(url)

    try:
        # Use the user provided encoding and in case
        # we get an error, default to UTF-8 classic
        parser = utilities.SafeParser(url, encoding=encoding)
    except UnicodeError:
        parser = utilities.SafeParser(url, encoding='utf-8')

    scheme, netloc, path, params, query, fragment = parser.get_url_parts

    key_values = parse_qsl(query, keep_blank_values=keep_blank_values)
    print(utilities.parse_qsl_to_bytes(
        query, keep_blank_values=keep_blank_values))
    key_values.sort()
    query = urlencode(key_values)

    unquoted_path = utilities.unquote_path(path)
    path = quote(unquoted_path, constants.PATH_SAFE_CHARACTERS) or '/'

    fragment = '' if not keep_fragments else fragment
    # print(unquoted_path)

    return urlunparse(
        (
            scheme,
            netloc.lower().rstrip(':'),
            path,
            params,
            query,
            fragment
        )
    )


class URL:
    def __init__(self, value):
        self._url = clean_url(value)

    def __repr__(self):
        return f'<URL: {self._url}>'

    def __str__(self):
        return self._url

    def __eq__(self, value):
        if isinstance(value, URL):
            return value._url == self._url
        return value == self._url


# # url = 'http://www.example.org/r%E9sum%E9.xml#r&#xE9;sum&#xE9;'
# url = 'http://www.example.org/something/here?google=1&a=2'
# c = clean_url(url)
# # print(c)
