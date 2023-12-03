import dataclasses
import pathlib
from re import Match
from typing import Any, Literal, Type, Union
from urllib.parse import ParseResult, ParseResultBytes


def safe_url_string(
    url: str,
    encoding: str = Literal['utf-8'],
    path_encoding: str = Literal['utf-8'],
    quote_path: bool = ...
) -> str: ...


def safe_download_url(
    url: str, encoding: str = Literal['utf-8'], path_encoding: str = Literal['utf-8']) -> str: ...


def is_url(value: str) -> bool: ...


def get_url_parameter(
    url: str,
    name: str,
    default: str = None,
    keep_blank_values: bool = False
) -> Union[str, None, Any]: ...


@dataclasses.dataclass
class URLParameter:
    key: str
    value: str

    def join(self) -> str: ...
    def replace(self, value: str) -> None: ...
    def deconstruct(self) -> tuple[str, str]: ...


def clean_url_query_parameters(
    url: str,
    names: list = ...,
    separator: str = Literal['&'],
    key_value_separator: str = Literal['='],
    unique: bool = True,
    keep_fragments: bool = False
) -> str: ...


def add_or_replace_parameter(url: str, params: dict = ...) -> str: ...


def path_to_file_uri(path: str) -> str: ...


def file_uri_to_path(url: str) -> str: ...


def convert_to_uri(url: str) -> Union[ParseResultBytes, str]: ...


def clean_url(
    url: str,
    keep_blank_values: bool = True,
    keep_fragments: bool = False,
    encoding: str = Literal['utf-8']
) -> str: ...


class URL:
    raw_url: str = ...
    url_object: ParseResult = ...

    def __init__(self, url_string: str): ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __eq__(self, obj) -> bool: ...
    def __add__(self, obj: Union[str, URL]) -> str: ...
    def __contains__(self, obj: Union[str, URL]) -> bool: ...
    def __hash__(self) -> int: ...
    def __len__(self) -> int: ...
    @property
    def is_path(self) -> bool: ...
    @property
    def is_valid(self) -> bool: ...
    @property
    def has_fragment(self) -> bool: ...
    @property
    def is_file(self) -> bool: ...
    @property
    def as_path(self) -> pathlib.Path: ...
    @property
    def get_extension(self) -> Union[str, None]: ...
    @property
    def url_stem(self) -> str: ...
    @classmethod
    def create(cls, url: str) -> Type[URL]: ...
    def is_same_domain(self, url: str) -> bool: ...
    def get_status(self) -> Union[bool, int]: ...
    def compare(self, url_to_compare: str) -> bool: ...
    def capture(self, regex: str) -> Union[Match, bool]: ...
    def test_path(self, regex: str) -> bool: ...
    def decompose_path(self, exclude: list = ...) -> list[str]: ...