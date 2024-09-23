import os
import subprocess
from asyncio import sleep

from rich import box
from rich.table import Table
from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Label

from ._data import SlurmData


class PartitionsUtilizationViewer(Widget):

    DEFAULT_CSS = """
    PartitionsUtilizationViewer {
        width: 60%;
        border: round;
    }
    VerticalScroll {
        scrollbar-size: 1 1;
        scrollbar-background: black 0%;
    }
    """
    BORDER_TITLE = "SINFO"

    def __init__(self, slurm: SlurmData):
        super().__init__()
        self.sinfo = slurm.sinfo_data
        self.squeue = slurm.squeue_data
        self.loading = True  # Flag to indicate loading state

    def compose(self) -> ComposeResult:
        yield VerticalScroll(Label())

    def on_mount(self):
        self.set_interval(5.0, self.refresh_viewer)
        self.refresh_viewer()

    @work  # Make sure this runs asynchronously
    async def refresh_viewer(self):
        self.sinfo.refresh_data()
        partition_table = Table(
            show_header=True,
            header_style="bold",
            box=None,
            padding=(0, 1),
            expand=True,
        )

        bar_width = 25

        partition_table.add_column(
            "Partition", justify="left", style="cyan", no_wrap=True
        )
        partition_table.add_column("Load")
        partition_table.add_column("[notbold][red]Alloc", justify="right", no_wrap=True)
        partition_table.add_column("[green]Idle", justify="right", no_wrap=True)
        partition_table.add_column("[orange1]Other", justify="right", no_wrap=True)
        partition_table.add_column("Total", justify="right", no_wrap=True)

        partitions = self.sinfo.data
        for partition in partitions:
            p_name, p_alloc, p_idle, p_other, p_ratio_usage = partition

            p_total = p_alloc + p_idle + p_other
            p_alloc_rs = int(p_alloc / p_total * bar_width)
            p_idle_rs = int(p_idle / p_total * bar_width)
            p_other_rs = bar_width - p_alloc_rs - p_idle_rs

            p_bar = (
                "[white]["
                + "[red]|" * p_alloc_rs
                + "[green]|" * p_idle_rs
                + "[orange1]." * p_other_rs
                + f"""{p_ratio_usage}%""".rjust(6)
                + "[white]]"
            )
            partition_table.add_row(
                p_name, p_bar, str(p_alloc), str(p_idle), str(p_other), str(p_total)
            )

        text = self.query_one(Label)
        text.update(partition_table)
        self.loading = False  # Flag to indicate loading state
