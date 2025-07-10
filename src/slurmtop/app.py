import argparse

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.theme import Theme
from textual.widgets import Footer, Label, Markdown, Static, TabbedContent, TabPane

import slurmtop

from .data import SlurmData, get_version_text
from .widgets import (
    InfoLine,
    PartitionsUtilizationViewer,
    SqueueMetricsViewer,
    SqueueViewer,
)


def run(argv=None):
    parser = argparse.ArgumentParser(
        description="Command-line Slurm monitor.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=get_version_text(),
        help="display version information",
    )

    args = parser.parse_args(argv)
    app = SlurmtopApp()
    app.run()


class SlurmtopApp(App):

    CSS_PATH = "styles/base.css"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.slurm = SlurmData()
        self.theme = "tokyo-night"

    def compose(self) -> ComposeResult:
        yield InfoLine()
        yield PartitionsUtilizationViewer(self.slurm)
        yield SqueueViewer(self.slurm)
        yield Footer()
