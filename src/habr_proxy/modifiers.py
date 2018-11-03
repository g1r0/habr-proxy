# coding: utf-8
from abc import ABCMeta
from abc import abstractmethod
from operator import methodcaller
from typing import Any
from typing import AnyStr
from typing import Iterable
from typing import List
from typing import Match
from typing import Pattern
from typing import Type
import re

from mitmproxy import ctx


def get_tm_transform_re() -> Pattern[AnyStr]:
    """Get compiled Tm transformation regex."""
    # base rule for 6-letter word
    word = r'([^\W\d_]{6})'

    # negative look ahead
    delimiters = r'.,:;'
    close_literals = r'\)\]\}\'\”\"`»/\\'

    word_continue = f'[^\\s<{close_literals}{delimiters}]+'
    close_tag = r'[^<]*?>'
    word_delimiter = f'[{delimiters}][^\\s<]+'
    negative_ahead = f'(?!{word_continue}|{close_tag}|{word_delimiter})'

    # negative look behind
    open_literals = r'\(\[\{\'\”\"`«/\\'

    word_begin = f'[^\\s>{open_literals}]{{1}}'
    open_tag = r'<'
    negative_behind = f'(?<!{word_begin}|{open_tag})'

    return re.compile(f'{negative_behind}{word}{negative_ahead}', re.DOTALL)


class BaseTransformAction(metaclass=ABCMeta):

    """Base action class for content transformation."""

    def __init__(self, content: Any) -> None:  # noqa: D107
        super().__init__()
        self.content = content

    @abstractmethod
    def transform(self) -> Any:
        """Abstract method to define data change."""
        raise NotImplementedError()


class BaseTransformHtmlAction(BaseTransformAction):

    """Base action class for HTML content transformation."""

    @abstractmethod
    def transform(self) -> str:
        """Abstract method to define data change."""
        raise NotImplementedError()

    @staticmethod
    def _get_paired_tag_re(tag: str) -> Pattern[AnyStr]:
        """Build paired tag regex."""
        regex = r'(<[\s]*placeholder[^>]*>.*?<[\s]*?/placeholder[\s]*?>)'
        regex = regex.replace('placeholder', tag, 2)

        return re.compile(regex, re.DOTALL)

    @staticmethod
    def _remove_intersected_matches(
            matches: List[Match[AnyStr]]) -> List[Match[AnyStr]]:
        """Ensure tag's regex matches not to be intersected."""
        if len(matches) < 2:
            return matches

        key_func = methodcaller('start', 0)
        matches.sort(key=key_func)

        not_intersected_matches = [matches[0]]
        for i in range(1, len(matches)):
            if matches[i].start(0) > matches[i-1].end(0):
                not_intersected_matches.append(matches[i])

        return not_intersected_matches


class TmTransformHtmlAction(BaseTransformHtmlAction):

    """Transformation scenario for 6-letter words with ™ mark.

    :Example: python -> python™
    """

    transform_re = get_tm_transform_re()

    # paired tags with content to be excluded from transformations
    excluded_tags = ('script', 'iframe')

    def __init__(self, content: str) -> None:  # noqa: D107
        super().__init__(content)
        self.excluded_matches = []
        self._collect_excluded_tags()
        self.excluded_matches = self._remove_intersected_matches(
            self.excluded_matches)

    def _collect_excluded_tags(self) -> None:
        """Gather skipped tag's match objects."""
        self.excluded_matches = []
        for tag in self.excluded_tags:
            tag_re = self._get_paired_tag_re(tag=tag)
            match_objects = tag_re.finditer(self.content)
            self.excluded_matches.extend(match_objects)

    def transform(self) -> str:
        """Modify words of HTML content."""
        def word_tm(match_object):
            """Change word -> word™."""
            word = match_object.group(0)

            return word + '™'

        result = []
        start_index = 0
        for match in self.excluded_matches:
            transformable_substring = self.content[start_index:match.start(0)]
            result.extend((
                self.transform_re.sub(word_tm, transformable_substring),
                match.group(0)
            ))
            start_index = match.end(0)

        transformable_substring = self.transform_re.sub(
            word_tm, self.content[start_index:])
        result.append(transformable_substring)

        return ''.join(result)


class UrlTransformHtmlAction(BaseTransformHtmlAction):

    """Transformation scenario for URL links to point on HabrProxy."""

    url_re = re.compile(r'(?<=href=")(https://habr.com)')

    def __init__(self, content: str) -> None:
        """Initialize action with parsed HTML content."""
        super().__init__(content)
        self.link_matches = None
        self._collect_links()

    def _collect_links(self) -> None:
        """Gather <a></a> tag match objects."""
        self.link_matches = []
        tag_re = self._get_paired_tag_re(tag='a')
        match_objects = tag_re.finditer(self.content)
        self.link_matches.extend(match_objects)

    def transform(self) -> str:
        """Modify links in HTML content to stay at habr-proxy."""
        replace_str = self._get_replace_url()

        result = []
        start_index = 0
        for match in self.link_matches:
            constant_substring = self.content[start_index:match.start(0)]
            result.extend((
                constant_substring,
                self.url_re.sub(replace_str, match.group(0))
            ))
            start_index = match.end(0)

        constant_substring = self.content[start_index:]
        result.append(constant_substring)

        return ''.join(result)

    @staticmethod
    def _get_replace_url() -> str:
        """Collect replace url from config."""
        options = dict(ctx.options.items())
        port = options['listen_port']
        replace_str = f'http://127.0.0.1:{port.value}'

        return replace_str


class BaseModificationManager(metaclass=ABCMeta):

    """Base manager class for content modification."""

    @abstractmethod
    def process(self, content: Any) -> Any:
        """Abstract method to process data content."""
        raise NotImplementedError()


class HTMLModificationManager(BaseModificationManager):

    """HTML content modification manager."""

    def __init__(
        self,
        actions: Iterable[Type[BaseTransformAction]]
    ) -> None:  # noqa: D107
        super().__init__()
        self.actions = actions

    def process(self, content: str) -> str:
        """Run series of transformations on HTML content."""
        for action in self.actions:
            step = action(content)
            content = step.transform()

        return content
