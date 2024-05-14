import os
import subprocess

from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widget import Widget


def get_partitions_list(num_partitions: int):
    partitions = []
    bashCommand = "sinfo -sh"
    process = subprocess.run(
        bashCommand, shell=True, stdout=subprocess.PIPE, encoding="utf-8"
    )
    output = process.stdout.splitlines()
    for ln in output:
        ln = ln.split()
        partitions.append(ln)

    return partitions[:num_partitions]


class PartitionsList(Widget):

    DEFAULT_CSS = """
    PartitionsList {
        width: auto;
        border: round;
    }
    """
    BORDER_TITLE = "SINFO"

    def on_mount(self):
        self.max_num_partitions = 20
        self.collect_data()
        self.set_interval(6.0, self.collect_data)

    def collect_data(self):
        partitions = get_partitions_list(self.max_num_partitions)

        table = Table(
            show_header=True,
            header_style="bold",
            box=None,
            padding=(0, 1),
            expand=True,
        )
        bar_width = 30

        table.add_column("Partition", justify="left", style="cyan", no_wrap=True)
        table.add_column("Load")
        table.add_column("[notbold][red]Alloc", justify="right", no_wrap=True)
        table.add_column("[green]Idle", justify="right", no_wrap=True)
        table.add_column("[orange1]Other", justify="right", no_wrap=True)
        table.add_column("Total", justify="right", no_wrap=True)

        # "allocated/idle/other/total"
        for partition in partitions:
            p_name = partition[0][:8]
            p_alloc, p_idle, p_other, p_total = [
                eval(i) for i in partition[3].split("/")
            ]
            p_alloc_rs = int(p_alloc / p_total * bar_width)
            p_idle_rs = int(p_idle / p_total * bar_width)
            p_other_rs = bar_width - p_alloc_rs - p_idle_rs
            p_ratio_usage = round((p_alloc + p_other) / p_total * 100, 2)

            p_bar = (
                "[white]["
                + "[red]|" * p_alloc_rs
                + "[green]|" * p_idle_rs
                + "[orange1]." * p_other_rs
                + f"""{p_ratio_usage}%""".rjust(6)
                + "[white]]"
            )

            table.add_row(
                p_name, p_bar, str(p_alloc), str(p_idle), str(p_other), str(p_total)
            )

        self.table = table

        self.refresh()

    def render(self) -> Panel:
        return self.table
