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
from textual.widgets import DataTable

from slurmtop.data import SlurmData


class PartitionsUtilizationViewer(Widget):

    CSS_PATH = "styles/base.css"
    BORDER_TITLE = "SINFO"

    def __init__(self, slurm: SlurmData):
        super().__init__()
        self.sinfo = slurm.sinfo_data

    def compose(self) -> ComposeResult:
        yield DataTable(
            cursor_type="none",
        )

    def on_mount(self):
        self.loading = True
        self.refresh_viewer()

    @work  # Make sure this runs asynchronously
    async def refresh_viewer(self):
        self.sinfo.refresh_data()

        partition_table = self.query_one(DataTable)

        terminal_width = os.get_terminal_size().columns
        viewer_width = terminal_width - 3
        if viewer_width < 62:
            viewer_width = 62

        bar_width = viewer_width - 50

        partition_table.add_column("Partition")
        partition_table.add_column("Load")
        partition_table.add_column("[notbold][red]Alloc")
        partition_table.add_column("[green]Idle")
        partition_table.add_column("[orange1]Other")
        partition_table.add_column("Total")

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

            if len(p_name) > 12:
                p_name = p_name[:10] + ".."

            partition_table.add_row(
                p_name, p_bar, str(p_alloc), str(p_idle), str(p_other), str(p_total)
            )

        self.loading = False
