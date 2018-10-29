# coding: utf-8
import pathlib

from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.tools.main import cmdline
from mitmproxy.tools.main import run

from habr_proxy.addons import ModifyHTMLContent
from habr_proxy.modifiers import HTMLModificationManager
from habr_proxy.modifiers import TmTransformHtmlAction
from habr_proxy.modifiers import UrlTransformHtmlAction


CONFIG_DIR = pathlib.Path(__file__).cwd().joinpath('..', 'config').as_posix()


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
    proxy = run(HabrDumpMaster, cmdline.mitmdump, ('--confdir', CONFIG_DIR))
