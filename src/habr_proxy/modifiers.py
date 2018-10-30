# coding: utf-8
from abc import ABCMeta
from abc import abstractmethod
import re
import typing

from bs4 import BeautifulSoup
from mitmproxy import ctx


class BaseTransformAction(metaclass=ABCMeta):

    """Base action class for content transformation."""

    def __init__(self, content: typing.Any) -> None:  # noqa: D107
        super().__init__()
        self.content = content

    @abstractmethod
    def transform(self) -> typing.Any:
        """Abstract method to define data change."""
        raise NotImplementedError()


class TmTransformHtmlAction(BaseTransformAction):

    """Transformation scenario for 6-letter words with ™ mark.

    :Example: python -> python™
    """

    word_re = re.compile(r'([^\w\-\(\[][\w]{6})(?![^<]*>|[\w.@#%\-])')

    def transform(self) -> str:
        """Modify words of HTML content."""
        def word_tm(match):
            """Change word -> word™."""
            word = match.group(0)

            return word + '™'

        return self.word_re.sub(word_tm, self.content)


class UrlTransformHtmlAction(BaseTransformAction):

    """Transformation scenario for URL links to point on HabrProxy."""

    url_re = re.compile(r'^https://habr.com')

    def __init__(self, content: str) -> None:
        """Initialize action with parsed HTML content."""
        super().__init__(content)
        self.soup = BeautifulSoup(content, 'html.parser')

    def transform(self) -> str:
        """Modify links in HTML content to stay at habr-proxy."""
        options = dict(ctx.options.items())
        port = options['listen_port']
        replace_str = f'http://127.0.0.1:{port.value}'

        links = self.soup.find_all('a')
        for link in links:
            link['href'] = self.url_re.sub(replace_str, link.get('href', ''))

        return self.soup.decode()


class BaseModificationManager(metaclass=ABCMeta):

    """Base manager class for content modification."""

    @abstractmethod
    def process(self, content: typing.Any) -> typing.Any:
        """Abstract method to process data content."""
        raise NotImplementedError()


class HTMLModificationManager(BaseModificationManager):

    """HTML content modification manager."""

    def __init__(
        self,
        actions: typing.Iterable[typing.Type[BaseTransformAction]]
    ) -> None:  # noqa: D107
        super().__init__()
        self.actions = actions

    def process(self, content: str) -> str:
        """Run series of transformations on HTML content."""
        for action in self.actions:
            step = action(content)
            content = step.transform()

        return content
