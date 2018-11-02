# coding: utf-8
from typing import Iterable
from typing import Tuple
from typing import Type

from src.habr_proxy.modifiers import BaseTransformAction
from src.habr_proxy.modifiers import TmTransformHtmlAction
from src.habr_proxy.modifiers import UrlTransformHtmlAction


def verify_test_data(
        action: Type[BaseTransformAction],
        data: Iterable[Tuple[str, str]]
) -> None:
    """Verify data combinations using extra spaces."""
    for input_data, expected_result in data:
        assert action(input_data).transform() == expected_result

        # also try combinations with extra spaces
        input_data = ' ' + input_data
        expected_result = ' ' + expected_result
        assert action(input_data).transform() == expected_result

        input_data = input_data + ' '
        expected_result = expected_result + ' '
        assert action(input_data).transform() == expected_result

        input_data = ' ' + input_data + ' '
        expected_result = ' ' + expected_result + ' '
        assert action(input_data).transform() == expected_result


class TestTmTransform:

    """Check transformations for 6-letter words with ™ mark."""

    action = TmTransformHtmlAction

    def test_word_rule(self) -> None:
        """Check single 6-letter word transformation."""
        test_sets = (
            ('change', 'change™'),
            ('nochange', 'nochange'),
            ('nochangenochange', 'nochangenochange'),
            ('noedit-nochange', 'noedit-nochange'),
            ('noedit.nochange', 'noedit.nochange'),
            ('noedit@nochange', 'noedit@nochange'),
            ('Семёно', 'Семёно™'),
            ('ch1nge', 'ch1nge'),
            ('(change)', '(change™)'),
            ('"change"', '"change™"'),
            ("'change'", "'change™'"),
            ('`change`', '`change™`'),
            ('[change]', '[change™]'),
            ('{change}', '{change™}'),
            ('[change/change]', '[change™/change™]'),
            (r'[change\change]', r'[change™\change™]'),
            ('«change»', '«change™»'),
            ('« change »', '« change™ »'),
        )

        verify_test_data(action=self.action, data=test_sets)

    def test_tag_definitions(self) -> None:
        """Check no content changed in tag definitions (between <>)."""
        test_sets = (
            ('<noedit>', '<noedit>'),
            ('< noedit >', '< noedit >'),
            ('</noedit >', '</noedit >'),
            ('</ noedit>', '</ noedit>'),
            (
                'change<noedit>change<noedit/ noedit > Семёно',
                'change™<noedit>change™<noedit/ noedit > Семёно™',
            ),
            (
                'change< noedit noedit>change<noedit/ noedit > Семёно',
                'change™< noedit noedit>change™<noedit/ noedit > Семёно™',
            ),
        )

        verify_test_data(action=self.action, data=test_sets)

    def test_excluded_tags(self) -> None:
        """Check no content is modified in excluded tags."""
        test_sets = (
            (
                '<noedit>change<script noedit>noedit< /script>< /noedit>',
                '<noedit>change™<script noedit>noedit< /script>< /noedit>',
            ),
            (
                '''<noedit>change
                    < iframe noedit>
                        noedit
                        <script noedit>
                            noedit
                        < /script>
                        noedit
                    </iframe>change
                < /noedit>''',
                '''<noedit>change™
                    < iframe noedit>
                        noedit
                        <script noedit>
                            noedit
                        < /script>
                        noedit
                    </iframe>change™
                < /noedit>''',
            ),
        )

        verify_test_data(action=self.action, data=test_sets)


class PinnedUrlTransformHtmlAction(UrlTransformHtmlAction):

    @staticmethod
    def _get_replace_url() -> str:
        """Pin replace URL string for test."""
        return 'http://127.0.0.1:8080'


class TestUrlTransform:

    """Check URL transformations for <a> tags."""

    action = PinnedUrlTransformHtmlAction

    def test_url_replace(self) -> None:
        """Check url transformation within <a> tag."""
        test_sets = (
            (
                '''<li>
                    <a href="https://habr.com/company/yandex/"
                        onclick="https://habr.com/company/yandex/"
                        rel="nofollow">
                        https://habr.com/company/yandex/
                    </a>
                </li>''',
                '''<li>
                    <a href="http://127.0.0.1:8080/company/yandex/"
                        onclick="https://habr.com/company/yandex/"
                        rel="nofollow">
                        https://habr.com/company/yandex/
                    </a>
                </li>''',
            ),
        )

        verify_test_data(action=self.action, data=test_sets)
