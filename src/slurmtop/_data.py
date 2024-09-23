import json
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, List

from rich import box
from rich.table import Table
from rich.text import Text


class SlurmData:
    """Data Wrapper"""

    def __init__(self):
        self.squeue_data = SqueueData()
        self.sinfo_data = SinfoData()


class SinfoData:
    """Handles data retrieval and processing for the partition status list."""

    def __init__(self):
        self.data_raw = []
        self.data = []
        self.refresh_data()  # refresh data_raw & data

    def fetch_data(self) -> List[str]:
        """Fetch the raw data directly from sinfo cmd"""
        try:
            bash_command = "sinfo -sh"
            process = subprocess.run(
                bash_command, shell=True, stdout=subprocess.PIPE, encoding="utf-8"
            )
            output = process.stdout.splitlines()
            data_raw = [line.split() for line in output]
            return data_raw
        except subprocess.CalledProcessError as e:
            print(f"Error fetching data: {e}")
            return []

    def process_data(self) -> List[List[int]]:
        """Process the raw data to provide a practical partition list"""
        data = []
        for partition in self.data_raw:
            p_name = partition[0][:]
            p_alloc, p_idle, p_other, p_total = [
                eval(i) for i in partition[3].split("/")
            ]
            p_ratio_usage = round((p_alloc + p_other) / p_total * 100, 2)
            data.append([p_name, p_alloc, p_idle, p_other, p_ratio_usage])
        return data

    def refresh_data(self):
        self.data_raw = self.fetch_data()
        self.data = self.process_data()


class SqueueData:
    """Handles data retrieval and processing for the job list."""

    def __init__(self):
        # Define the keys to be selected for display
        self.keys = [
            "job_id",
            "partition",
            "name",
            "user_name",
            "job_state",
            "time_elapse",
            "node_number",
            "nodes",
            "priority_number",
        ]
        # Load initial job data
        self.jobs = []
        self.refresh()

    def fetch_squeue_data(self) -> List[Dict]:
        """Fetches the raw job list using the squeue command."""
        try:
            bash_command = "squeue --json"
            process = subprocess.run(
                bash_command, shell=True, stdout=subprocess.PIPE, encoding="utf-8"
            )
            data = json.loads(process.stdout)  # Load JSON output
            return data["jobs"]  # Extract the list of jobs from the JSON response
        except subprocess.CalledProcessError as e:
            print(f"Error fetching data: {e}")
            return []

    def process_job_data(self, jobs: List[Dict], max_jobs: int = None) -> List[Dict]:
        """Process the raw data to provide a practical job list ready to visualize."""
        processed_jobs = []
        for job in jobs:
            # Compute and format "Time"
            job["node_number"] = job["node_count"]["number"]
            job["priority_number"] = job["priority"]["number"]
            job["job_state"] = job["job_state"][0]

            # Get start time (time_t type) and subtract it to current time
            # Generate a human readable time elapse like dd:hh:mm:ss
            if job["start_time"]["number"] > 0:
                start_time = datetime.fromtimestamp(job["start_time"]["number"])
                end_time = datetime.now()
                if end_time < start_time:
                    time_elapse = ""
                else:
                    time_elapse = str(end_time - start_time).split(".")[0]
            else:
                time_elapse = ""

            job["time_elapse"] = time_elapse

            processed_job = {
                key: (str(job.get(key))[:17] + "...")
                if len(str(job.get(key))) > 20
                else str(job.get(key, ""))
                for key in self.keys
            }
            processed_jobs.append(processed_job)

        return processed_jobs if max_jobs is None else processed_jobs[:max_jobs]

    def refresh(self):
        self.jobs = self.process_job_data(self.fetch_squeue_data())


def time_to_seconds(time_str: str) -> int:
    """Convert time string in D-HH:MM:SS, HH:MM:SS, or MM:SS format to total seconds."""
    try:
        # If the format includes days, D-HH:MM:SS
        if "-" in time_str:
            days, time_part = time_str.split("-")
            time_obj = datetime.strptime(time_part, "%H:%M:%S")
            return (
                int(days) * 86400
                + time_obj.hour * 3600  # Days to seconds
                + time_obj.minute * 60
                + time_obj.second
            )
        # If the format is HH:MM:SS
        elif time_str.count(":") == 2:
            time_obj = datetime.strptime(time_str, "%H:%M:%S")
            return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
        # If the format is MM:SS
        elif time_str.count(":") == 1:
            time_obj = datetime.strptime(time_str, "%M:%S")
            return time_obj.minute * 60 + time_obj.second
    except ValueError:
        # In case of an invalid time format, return 0 as fallback
        return 0
