import dataclasses
import os
import posixpath
from urllib.parse import (parse_qs, parse_qsl, quote, unquote, urldefrag,
                          urlparse, urlsplit, urlunsplit)
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
        path = constants.PARENT_DIRECTORIES.sub('', posixpath.normpath(url_object.path))
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
    seen_keys = []



def path_to_file_uri(path) :
    result = pathname2url(os.path.abspath(path))
    return f"file:///{result.lstrip('/')}"


def file_uri_to_path(url):
    url_path = urlparse(url).path
    return url2pathname(url_path)
