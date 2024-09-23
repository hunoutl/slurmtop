import json
import re
import subprocess
from asyncio import sleep
from datetime import datetime, timedelta

from rich.table import Table
from textual import work
from textual.app import App, ComposeResult
from textual.events import Click
from textual.widget import Widget
from textual.widgets import DataTable, Label

from ._data import SlurmData, SqueueData


class SqueueViewer(Widget):
    """Viewer Widget for SQUEUE, generate a datatable for all jobs running on slurm"""

    BORDER_TITLE = "SQUEUE"
    DEFAULT_CSS = """
    SqueueViewer {
        height: 100%;
        width: 100%;
        border: round #33ffbe;
    }
    DataTable {
        scrollbar-size: 1 1;
        scrollbar-background: black 0%;
    }
    """

    def __init__(self, slurm: SlurmData):
        super().__init__()
        self.squeue = slurm.squeue_data
        self.current_sorts = {}  # Dictionary to keep track of sorting order
        self.sorted_column = None  # Track the currently sorted column
        self.sorted_order = (
            None  # Track the current order (True for ascending, False for descending)
        )
        self.loading = True  # Flag to indicate loading state

    def compose(self) -> ComposeResult:
        yield DataTable(cursor_type="row")

    def on_mount(self) -> None:
        """Start loading data when the widget is mounted."""
        # self.set_interval(5.0, self.refresh_viewer)
        self.refresh_viewer(refresh_data=True)  # Trigger the async data loading task

    @work  # Make sure this runs asynchronously
    async def refresh_viewer(self, refresh_data: bool = False) -> None:
        """Simulate loading data asynchronously."""
        data_table = self.query_one(DataTable)

        if refresh_data:
            self.squeue.refresh()
        jobs = self.squeue.jobs  # Fetch jobs using SqueueData

        data_table.clear(columns=True)  # Clear existing columns and data

        # Columns to display
        columns = self.squeue.keys

        # Add columns with current sort order indicator if applicable
        for column in columns:
            data_table.add_column(f"{column}", key=column)

        # Add rows
        for job in jobs:
            row = [self.format_value(job, col) for col in columns]
            data_table.add_row(*row)

        self.loading = False  # Data has been loaded, stop loading indicator

    def format_value(self, job: dict, key: str) -> str:
        """Format the value based on the key."""
        return job.get(key, "N/A")

    def sort_reverse(self, column: str) -> bool:
        """Toggle and return the reverse sorting order for the specified column."""
        self.current_sorts[column] = not self.current_sorts.get(column, False)
        return self.current_sorts[column]

    def sort(self, column: str) -> None:
        """Sort the DataTable by the specified column."""

        self.sorted_column = column
        self.sorted_order = not self.current_sorts.get(column, False)

        if column == "time_elapse":
            self.action_sort_by_time(column)
        elif column == "node_number":
            self.action_sort_by_number(column)
        else:
            self.action_sort_by_string(column)

    def action_sort_by_time(self, column: str) -> None:
        """Sort DataTable by time used in D-HH:MM:SS, HH:MM:SS"""
        table = self.query_one(DataTable)
        table.sort(
            column,
            key=lambda column: datetime_to_seconds(
                column
            ),  # Convert time to total seconds for sorting
            reverse=self.sort_reverse(column),
        )

    def action_sort_by_string(self, column: str) -> None:
        """Sort DataTable by specific key."""
        table = self.query_one(DataTable)
        table.sort(
            column,
            key=lambda column: column,
            reverse=self.sort_reverse(column),
        )

    def action_sort_by_number(self, column: str) -> None:
        """Sort DataTable by specific key."""
        table = self.query_one(DataTable)
        table.sort(
            column,
            key=lambda column: int(column),
            reverse=self.sort_reverse(column),
        )

    def on_data_table_header_selected(self, event: Click) -> None:
        """Sort `DataTable` items by the clicked column header."""
        column_name = event.label.plain.split()[0]
        self.sort(column_name)  # Extract the column name without the sort indicator


class SqueueMetricsViewer(Widget):
    """SQUEUE Overview vizualisation widget, display queue metrics"""

    BORDER_TITLE = "SQUEUE-METRICS"
    DEFAULT_CSS = """
    SqueueMetricsViewer {
        height: 100%;
        width: 40%;
        border: round #33ffbe;
    }
    """

    def __init__(self, slurm: SlurmData = None):
        super().__init__()
        self.slurm = slurm
        self.loading = True  # Flag to indicate loading state

    def compose(self) -> ComposeResult:
        yield Label()

    def on_mount(self) -> None:
        """Start loading data when the widget is mounted."""
        self.load_data()  # Trigger the async data loading task

    @work  # Make sure this runs asynchronously
    async def load_data(self) -> None:
        """Simulate loading data asynchronously."""
        await sleep(1)  # Simulate data fetching or processing delay
        jobs = self.slurm.squeue_data.jobs

        metrics_table = Table(
            show_header=True,
            header_style="bold",
            box=None,
            padding=(0, 1),
            expand=True,
        )

        metrics_table.add_column(
            "Partition", justify="left", style="cyan", no_wrap=True
        )
        metrics_table.add_column("Jobs-Ratio")
        metrics_table.add_column("[notbold][red]Running", justify="right", no_wrap=True)
        metrics_table.add_column("[orange1]Pending", justify="right", no_wrap=True)

        ratio_running_pending = "[red]█" * 10 + "[orange1]█" * 10
        metrics_table.add_row("cpu_p1", ratio_running_pending, "2500", "3000")

        label = self.query_one(Label)
        label.update(metrics_table)
        self.loading = False  # Data has been loaded, stop loading indicator


def datetime_to_seconds(time_str: str) -> int:
    if time_str == "":
        return 0

    # Regex pattern to capture "D days, HH:MM:SS", "D day, HH:MM:SS", or "HH:MM:SS"
    pattern = re.compile(
        r"(?:(\d+)\s+days?\s*,\s+|(?:(\d+)\s+day\s*,\s+))?(\d+):(\d+):(\d+)"  # "D days, HH:MM:SS" or "D day, HH:MM:SS" or "HH:MM:SS"
    )
    match = pattern.match(time_str)

    if not match:
        raise ValueError(f"Invalid time format: {time_str}")

    days = int(match.group(1) or 0)
    hours = int(match.group(3) or 0)
    minutes = int(match.group(4))
    seconds = int(match.group(5) or 0)

    # Convert all to total seconds
    total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
    return total_seconds
