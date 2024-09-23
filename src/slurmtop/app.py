import argparse
from sys import version_info

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Label, Markdown, TabbedContent, TabPane

from .__about__ import __version__
from ._data import SinfoData, SlurmData, SqueueData
from ._info_widget import InfoLine
from ._sinfo_widget import PartitionsUtilizationViewer
from ._squeue_widget import SqueueMetricsViewer, SqueueViewer


def _get_version_text():
    python_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    return "\n".join(
        [
            f"slurmtop {__version__} [Python {python_version}]",
            "Copyright (c) 2024 Léo Hunout (IDRIS/CNRS)",
        ]
    )


class SlurmtopApp(App):

    # CSS_PATH = "app.tcss"
    CSS = """
    Screen {
        layout: grid;
        grid-size: 1 3; /* Increase grid size */
        grid-rows: auto 2fr 4fr;
    }

    """

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.slurm = SlurmData()

    def compose(self) -> ComposeResult:
        yield InfoLine()

        yield Horizontal(
            PartitionsUtilizationViewer(self.slurm),
            # SqueueMetricsViewer(self.slurm),
        )
        yield SqueueViewer(self.slurm)
        yield Footer()


def run(argv=None):
    parser = argparse.ArgumentParser(
        description="Command-line Slurm monitor.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=_get_version_text(),
        help="display version information",
    )

    args = parser.parse_args(argv)
    app = SlurmtopApp()
    app.run()
