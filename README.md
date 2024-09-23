
<p align="center">
  <img src="https://raw.githubusercontent.com/hunoutl/slurmtop/fe90324367067f962ffebf0666dbaf7f5b4ad86d/imgs/slurmtop_logo.jpeg" width=640px alt="Slurmtop Logo" />
</p>

<p align="center">
  <i>slurmtop is a refreshing and intuitive terminal interface for monitoring SLURM clusters.</i><br>
  <i>Get an elegant, at-a-glance view of partitions and jobs to track cluster usage and performance, all from the comfort of your shell.</i>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/hunoutl/slurmtop/fe90324367067f962ffebf0666dbaf7f5b4ad86d/imgs/slurmtop_preview.png" alt="Slurmtop Preview" title="Slurmtop Preview" />
</p>



**slurmtop** is a TUI (terminal user interface) to monitor slurm partitions and jobs.
It is designed to provide a quick overview of the usage status of the slurm cluster.
slurmtop relies on [textualize](https://github.com/Textualize/textual) for display and fetches data via the [SLURM](https://slurm.schedmd.com/documentation.html) CLI.

## Installation

Install Slurmtop via pip:
```bash
pip install slurmtop
```

For development:
```bash
pip install -e .

```
