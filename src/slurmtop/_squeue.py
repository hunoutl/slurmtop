import subprocess
from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.widget import Widget
from textual.widgets import DataTable
from textual.app import App, ComposeResult


def split_string_into_lines(string, max_length):
    lines = []
    for i in range(0, len(string), max_length):
        lines.append(string[i:i+max_length])
    return '\n'.join(lines)

def get_jobs_list(num_jobs: int = None, sort: str = None ):
    bashCommand = "squeue --sort P,t"
    process = subprocess.run(bashCommand, shell=True, stdout=subprocess.PIPE, encoding='utf-8')
    data=process.stdout.splitlines()
    
    headers = data[0].split()
    jobs = []
    for row in data[1:]:
        row_dict = {}
        for header, value in zip(headers, row.split()):
            row_dict[header] = value
        jobs.append(row_dict)
        
    if num_jobs == None :
        return jobs
    else :
        return jobs[:num_jobs]




class JobsList(Widget):
    #BINDINGS = [("z", "sort", "Sort")]
    DEFAULT_CSS = """
    JobsList {
        height: 100%;
        width: 100%;
        border: round #33ffbe;
        }
    DataTable {
        scrollbar-size: 1 1;
        scrollbar-background: black 0%;
    }
    """
    BORDER_TITLE = "SQUEUE"

    def compose(self) -> ComposeResult:
        yield DataTable(cursor_type="row")

    def on_mount(self) -> None:
        jobs = get_jobs_list()
        
        table = self.query_one(DataTable)
        table.add_column("JOBID",width=8)
        table.add_column("PARTITION ▲")
        table.add_column("NAME")
        table.add_column("USER")
        table.add_column("S")
        table.add_column("TIME")
        table.add_column("NODES")
        table.add_column("NODELIST",width=30)

        for j in jobs:
            jobid = j.get("JOBID", "")
            partition = j.get("PARTITION","")
            name = j.get("NAME","")
            user = j.get("USER","")
            state = j.get("ST","")
            time = j.get("TIME","")
            nodes = j.get("NODES","")
            
            nodelist = j.get("NODELIST(REASON)","")
   
            table.add_row(
                jobid, partition, name, user, state, time, nodes, nodelist,height=None,
            )

















'''

class JobsList_old(Widget):


    def on_mount(self):
        self.max_num_jobs = 50
        self.collect_data()
        self.set_interval(8.0, self.collect_data)

    def collect_data(self):
        jobs = get_jobs_list(num_jobs=self.max_num_jobs)

        table = Table(
            show_header=True,
            header_style="bold",
            box=None,
            padding=(0, 1),
            expand=True,
        )
        # set ration=1 on all columns that should be expanded
        # <https://github.com/Textualize/rich/issues/2030>
        table.add_column(Text("JOBID", justify="left"), no_wrap=True)
        table.add_column("PARTITION", style="green", no_wrap=True)
        table.add_column("NAME", no_wrap=True)
        table.add_column("USER", no_wrap=True)
        table.add_column("STATE", no_wrap=True)
        table.add_column("TIME", no_wrap=True)
        table.add_column("NODES", no_wrap=True)
        table.add_column("NODELIST(REASON)", no_wrap=True)

        for j in jobs:
            # Everything can be None here, see comment above
            jobid = j.get("JOBID", "")
            partition = j.get("PARTITION","")
            name = j.get("NAME","")
            user = j.get("USER","")
            state = j.get("ST","")
            time = j.get("TIME","")
            nodes = j.get("NODES","")
            nodelist = j.get("NODELIST(REASON)","")
   
            table.add_row(
                jobid, partition, name, user, state, time, nodes, nodelist
            )

        #total_num_threads = sum((p["num_threads"] or 0) for p in processes)
        #num_sleep = sum(p["status"] == "sleeping" for p in processes)

        self.panel = Panel(
            table,
            title=f"SQUEUE",
            title_align="left",
            border_style="white",
            box=box.ROUNDED,
        )

        self.refresh()

    def render(self) -> Panel:
        return self.panel

'''