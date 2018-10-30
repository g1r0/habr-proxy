# coding: utf-8
import os

from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.tools.main import cmdline
from mitmproxy.tools.main import run

from habr_proxy.addons import ModifyHTMLContent
from habr_proxy.modifiers import HTMLModificationManager
from habr_proxy.modifiers import TmTransformHtmlAction
from habr_proxy.modifiers import UrlTransformHtmlAction


CONFIG_DIR_VAR = 'PROXY_CONFIG_DIR'

CONFIG_PATH = os.environ.get(CONFIG_DIR_VAR, None)
if CONFIG_PATH is None:
    raise ValueError(
        'Environment variable %s not found.' % CONFIG_DIR_VAR
    )


class HabrDumpMaster(DumpMaster):

    """Mitmdump mainloop object for habr-proxy."""

    def __init__(self, opts: options.Options) -> None:
        """Initialize extra addons."""
        super().__init__(opts)

        self.addons.add(
            ModifyHTMLContent(
                manager=HTMLModificationManager(
                    actions=(
                        TmTransformHtmlAction,
                        UrlTransformHtmlAction,
                    )
                )
            )
        )


if __name__ == "__main__":
    proxy = run(HabrDumpMaster, cmdline.mitmdump, ('--confdir', CONFIG_PATH))
