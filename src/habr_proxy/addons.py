# coding: utf-8
from mitmproxy import ctx
from mitmproxy.net.http import parse_content_type
from mitmproxy.utils import human
import mitmproxy

from habr_proxy.modifiers import BaseModificationManager


class ModifyHTMLContent:

    """Mitmdump scenario for HTML content modification."""

    def __init__(self, manager: BaseModificationManager) -> None:  # noqa: D107
        super().__init__()
        self.manager = manager

    def response(self, flow: mitmproxy.http.HTTPFlow):
        """Response processing.

        Full HTTP response has already been read here.
        """
        ident = (len(human.format_address(flow.client_conn.address)) - 2)

        if 'html' in parse_content_type(flow.response.headers['Content-type']):
            modified_content = self.manager.process(flow.response.text)
            flow.response.text = modified_content
            ctx.log.info(f'{" " * ident} << HTML modification done.')
