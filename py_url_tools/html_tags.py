import re
from html.entities import name2codepoint
from typing import Match

from py_url_tools import constants, utilities


class ReplaceEntities:
    """
    Replace entities in a given string

    >>> replace_entities(b'Price: &pound;100')
    ... "Price: £100"
    """

    def __call__(self, text, keep=[], **kwargs):
        encoding = kwargs.get('encoding', 'utf-8')
        return constants.ENTITY_REGEX.sub(
            self.convert,
            utilities.string_to_unicode(text, encoding=encoding)
        )

    def convert(self, value, keep=[], remove_illegal=False, encoding='utf-8'):
        if not isinstance(value, Match):
            raise ValueError

        regex_result = value.groupdict()
        number = None
        if regex_result.get('dec'):
            number = int(regex_result['dec'], 10)
        elif regex_result.get("hex"):
            number = int(regex_result['hex'], 16)
        elif regex_result.get('named'):
            entity_name = regex_result['named']
            if entity_name.lower() in keep:
                return value.group(0)
            else:
                number = (
                    name2codepoint.get(entity_name) or
                    name2codepoint.get(entity_name.lower())
                )

        if number is not None:
            try:
                if 0x80 <= number <= 0x9F:
                    return bytes((number,)).decode('cp1252')
                else:
                    return chr(number)
            except (ValueError, OverflowError):
                pass
        return '' if remove_illegal and value.get('semicolon') else value.group(0)


convert_entity = ReplaceEntities()
# print(convert_entity(b'Price: &pound;100'))
# print(convert_entity(b'Price: &pound;100'))


def has_entity(text, encoding='utf-8'):
    return constants.ENTITY_REGEX.search(
        utilities.string_to_unicode(text, encoding=encoding)
    )


def replace_html_tags(text, replacement_token='', encoding='utf-8'):
    return constants.HTML_TAG_REGEX.sub(
        replacement_token,
        utilities.string_to_unicode(text, encoding=encoding)
    )


def remove_comments(text, encoding='utf-8'):
    unicode_text = utilities.string_to_unicode(text, encoding)
    return constants.REMOVECOMMENTS_RE.sub('', unicode_text)


class RemoveHTMLTags:
    """
    Removes HTML tags from a given string

    >>> text = '<div><p><b>This is a link:</b> <a href="http://www.example.com">example</a></p></div>'
    ... "This is a link: example"
    """

    TAG_REGEX = "</?([^ >/]+).*?>"

    def __call__(self, text, which_ones=[], keep=[], encoding='utf-8'):
        regex = re.compile(self.TAG_REGEX, re.DOTALL | re.IGNORECASE)
        return regex.sub(self.remove_tag, utilities.string_to_unicode(text))

    @staticmethod
    def can_be_removed(tag):
        tag = tag.lower()
        # if which_ones:
        #     return tag in which_ones
        # else:
        #     return tag not in keep
        return True

    def remove_tag(self, value):
        if not isinstance(value, Match):
            raise ValueError

        tag = value.group(1)
        return '' if self.can_be_removed(tag) else value.group(0)


remove_html_tags = RemoveHTMLTags()


def remove_tags_with_content(text, which_ones=[], encoding=None):
    unicode_text = utilities.string_to_unicode(text, encoding=encoding)
    if which_ones:
        tags = "|".join(
            [rf"<{tag}\b.*?</{tag}>|<{tag}\s*/>" for tag in which_ones])
        regex = re.compile(tags, re.DOTALL | re.IGNORECASE)
        unicode_text = regex.sub("", unicode_text)
    return unicode_text


def replace_escape_chars(text, escape_characters=["\n", "\t", "\r"], replace_by='', encoding=None):
    unicode_text = utilities.string_to_unicode(text, encoding=encoding)
    for item in escape_characters:
        unicode_replacement_text = utilities.string_to_unicode(
            replace_by, encoding=encoding)
        unicode_text = unicode_text.replace(item, unicode_replacement_text)
    return unicode_text


def strip_html5_whitespace(text):
    return text.strip(constants.HTML5_WHITESPACE)
