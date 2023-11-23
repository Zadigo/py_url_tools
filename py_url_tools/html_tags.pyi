from ast import List
from typing import Any, Literal

class ReplaceEntities:
    def __call__(self, text: str, keep: list = ..., **kwargs: Any) -> str: ...

    def convert(
        self,
        value: str,
        keep: list = ...,
        remove_illegal: bool = False,
        encoding: str = Literal['utf-8']
    ) -> str: ...


convert_entity = ReplaceEntities()


def has_entity(text: str, encoding: str = Literal['utf-8']) -> bool: ...


def replace_html_tags(
    text: str,
    replacement_token='',
    encoding: str = Literal['utf-8']
) -> str: ...


def remove_comments(text: str, encoding: str = Literal['utf-8']) -> str: ...


class RemoveHTMLTags:
    TAG_REGEX: Literal["</?([^ >/]+).*?>"] = ...

    def __call__(
        self,
        text: str,
        which_ones: list = ...,
        keep: list = ...,
        encoding: str = Literal['utf-8']
    ) -> str: ...

    @staticmethod
    def can_be_removed(tag: str) -> bool: ...
    def remove_tag(self, value: str) -> str: ...


remove_html_tags = RemoveHTMLTags()


def remove_tags_with_content(
    text: str,
    which_ones: list = ...,
    encoding: str = ...
) -> str: ...


def replace_escape_chars(
    text: str,
    escape_characters: List = ...,
    replace_by: str = '',
    encoding: str = None
) -> str: ...


def strip_html5_whitespace(text: str) -> str: ...
