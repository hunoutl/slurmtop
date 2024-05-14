import getpass
import platform
import time
from datetime import datetime, timedelta
import subprocess
import os
import distro
import psutil
from rich.table import Table
from textual.widget import Widget
from textual.geometry import Size

class InfoLine(Widget):
    DEFAULT_CSS = """
    InfoLine {
        height: 1fr;
        border: round #33ffbe;
        }
    
    """
    BORDER_TITLE = "SLURMTOP"

    def on_mount(self):

        self.set_interval(1.0, self.refresh)

        username = getpass.getuser()
        ustring = f"{username}@"
        node = platform.node()
        if node:
            ustring += f"[b]{platform.node()}[/]"

        system = platform.system()
        if system == "Linux":
            ri = distro.os_release_info()
            system_list = [ri["name"]]
            if "version_id" in ri:
                system_list.append(ri["version_id"])
            #system_list.append(f"{platform.architecture()[0]}/ {platform.release()}")
            system_string = " ".join(system_list)
        else:
            # fallback
            system_string = ""
        
        result = subprocess.run(['sinfo', '-V'], capture_output=True, text=True, check=True)
        slurm_string = "/ Slurm "+result.stdout.split()[1]
        self.left_string = " ".join([ustring, system_string, slurm_string])

    def render(self):
        table = Table(show_header=False, box=None,width=os.get_terminal_size()[0]-2)

        table.add_column(justify="left")
        table.add_column(justify="right")
        table.add_row(
            self.left_string, datetime.now().strftime("%c")
        )
        return table


