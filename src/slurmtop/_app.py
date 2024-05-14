import argparse
from sys import version_info

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid
from textual.widgets import Footer, Placeholder

from .__about__ import __version__
from ._info import InfoLine
from ._sinfo import PartitionsList
from ._squeue import JobsList


def _get_version_text():
    python_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    return "\n".join(
        [
            f"slurmtop {__version__} [Python {python_version}]",
            "Copyright (c) 2024 Léo Hunout",
        ]
    )


# with a grid
class SlurmtopApp(App):

    CSS_PATH = "app.css"

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield InfoLine()
        yield PartitionsList()
        yield JobsList()
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
