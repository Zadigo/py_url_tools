import string
import re

RFC3986_GEN_DELIMITERS = b":/?#[]@"


RFC3986_SUB_DELIMITERS = b"!$&'()*+,;="


RFC3986_RESERVED = RFC3986_GEN_DELIMITERS + RFC3986_SUB_DELIMITERS


RFC3986_UNRESERVED = (
    string.ascii_letters +
    string.digits + "-._~"
).encode('ascii')


EXTRA_SAFE_CHARS = b"|"


RFC3986_USERINFO_SAFE_CHARS = RFC3986_UNRESERVED + RFC3986_SUB_DELIMITERS + b":"


SAFE_CHARACTERS = RFC3986_RESERVED + RFC3986_UNRESERVED + EXTRA_SAFE_CHARS + b"%"


PATH_SAFE_CHARACTERS = SAFE_CHARACTERS.replace(b"#", b"")

# % is currently excluded from these lists of characters, due to
# limitations of the current safe_url_string implementation, but it should also
# be escaped as %25 when it is not already being used as part of an escape
# character


USERINFO_SAFEST_CHARACTERS = RFC3986_USERINFO_SAFE_CHARS.translate(
    None,
    delete=b":;="
)

PATH_SAFEST_CHARACTERS = SAFE_CHARACTERS.translate(None, delete=b"#[]|")


SPECIAL_QUERY_SAFEST_CHARACTERS = PATH_SAFEST_CHARACTERS.translate(
    None, delete=b"'")


FRAGMENT_SAFEST_CHARS = PATH_SAFEST_CHARACTERS


DEFAULT_PORTS = {
    'ftp': 21,
    'file': None,
    'http': 80,
    'https': 443,
    'ws': 80,
    'wss': 443,
}


SPECIAL_SCHEMES = set(DEFAULT_PORTS.keys())


# https://infra.spec.whatwg.org/commit-snapshots/59e0d16c1e3ba0e77c6a60bfc69a0929b8ffaa5d/#code-points

ASCII_TAB_OR_NEWLINE = "\t\n\r"


ASCII_WHITESPACE = "\t\n\x0c\r "


C0_CONTROL = "".join(chr(x) for x in range(32))


C0_CONTROL_OR_SPACE = C0_CONTROL + " "


ASCII_DIGIT = string.digits


ASCII_HEX_DIGIT = string.hexdigits


ASCII_ALPHA = string.ascii_letters


ASCII_ALPHANUMERIC = string.ascii_letters + string.digits


ASCII_TAB_OR_NEWLINE_TRANSLATION_TABLE = {
    ord(x): None for x in ASCII_TAB_OR_NEWLINE
}


PARENT_DIRECTORIES = re.compile(r"/?(\.\./)+")
