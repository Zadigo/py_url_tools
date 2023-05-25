from py_url_tools import constants

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
