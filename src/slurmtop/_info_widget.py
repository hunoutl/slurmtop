import getpass
import os
import platform
import subprocess
import time
from asyncio import sleep
from datetime import datetime, timedelta

from rich.table import Table
from textual import work
from textual.app import ComposeResult
from textual.geometry import Size
from textual.widget import Widget
from textual.widgets import Label


def get_os_release_info():
    """Retrieve OS release info from /etc/os-release on Linux systems."""
    os_info = {}
    try:
        # Read /etc/os-release for Linux systems
        with open("/etc/os-release", "r") as f:

            for line in f:
                # Skip empty lines
                if not line.strip():
                    continue
                # Only process lines that contain an '='
                if "=" in line:
                    key, value = line.rstrip().split("=", 1)
                    os_info[key] = value.strip('"')
    except FileNotFoundError:
        os_info["NAME"] = "Unknown Linux"
        os_info["VERSION_ID"] = "Unknown Version"

    return os_info


class InfoLine(Widget):
    DEFAULT_CSS = """
    InfoLine {
        height: 1fr;
        border: round #33ffbe;
        }
    
    """
    BORDER_TITLE = "SLURMTOP"

    def __init__(self):
        super().__init__()
        self.loading = True

    def compose(self) -> ComposeResult:
        yield Label()

    def on_mount(self) -> None:
        """Start loading data when the widget is mounted."""
        self.set_interval(1.0, self.refresh_viewer)
        self.refresh_viewer()  # Trigger the async data loading task

    @work  # Make sure this runs asynchronously
    async def refresh_viewer(self) -> None:
        """Simulate loading data asynchronously."""
        # await sleep(1)  # Simulate data fetching or processing delay

        line = self.query_one(Label)

        username = getpass.getuser()
        ustring = f"{username}@"

        # Get machine node
        node = platform.node()
        if node:
            ustring += f"[b]{node}[/]"

        # Determine system
        system = platform.system()
        if system == "Linux":
            # Fetch OS release info on Linux systems
            ri = get_os_release_info()
            system_list = [ri.get("NAME", "Unknown Linux")]
            if "VERSION_ID" in ri:
                system_list.append(ri["VERSION_ID"])
            # Optionally, you can add architecture or platform release info
            # system_list.append(f"{platform.architecture()[0]}/ {platform.release()}")
            system_string = " ".join(system_list)
        else:
            # Fallback for non-Linux systems
            system_string = f"{system} {platform.release()}"

        result = subprocess.run(
            ["sinfo", "-V"], capture_output=True, text=True, check=True
        )
        slurm_string = "/ Slurm " + result.stdout.split()[1]
        self.left_string = " ".join([ustring, system_string, slurm_string])

        table = Table(show_header=False, box=None, width=os.get_terminal_size()[0] - 2)

        table.add_column(justify="left")
        table.add_column(justify="right")
        table.add_row(self.left_string, datetime.now().strftime("%c"))

        line.update(table)

        self.loading = False  # Data has been loaded, stop loading indicator
