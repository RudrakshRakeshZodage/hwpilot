"""Rich console output formatting for HwPilot CLI."""

import sys
from rich.console import Console
from rich.table import Table
from typing import Dict, Any
from hwpilot.models.hardware import SystemReport
from hwpilot.models.plan import InstallationPlan

# Ensure stdout and stderr handle UTF-8 on Windows legacy consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

console = Console()
DIVIDER = "----------------------------------------"


def print_banner():
    console.print()
    console.print("[bold cyan]HwPilot[/bold cyan]")
    console.print("[dim]Hardware-aware ML Environment Manager[/dim]")
    console.print(DIVIDER)


def print_section(title: str):
    console.print()
    console.print(DIVIDER)
    console.print(f"[bold gold1]{title}[/bold gold1]")
    console.print(DIVIDER)


def print_detection_report(report: SystemReport):
    print_banner()
    console.print("[bold cyan]Detecting system...[/bold cyan]\n")

    # CPU
    console.print("[bold white]CPU[/bold white]")
    console.print(f"  {report.cpu.model}")
    console.print(f"  Architecture: {report.cpu.architecture}")
    console.print(f"  Cores: {report.cpu.physical_cores}")
    console.print(f"  Threads: {report.cpu.logical_cores}")
    if report.cpu.ram_gb > 0:
        console.print(f"  RAM: {report.cpu.ram_gb:.1f} GB")
    console.print()

    # GPU
    console.print("[bold white]GPU[/bold white]")
    if report.gpu.available:
        console.print(f"  [green]{report.gpu.vendor} {report.gpu.model}[/green]")
        if report.gpu.vram_gb > 0:
            console.print(f"  VRAM: {report.gpu.vram_gb:.1f} GB")
        if report.gpu.compute_capability:
            console.print(f"  Compute Capability: {report.gpu.compute_capability}")
    else:
        console.print(f"  [yellow]{report.gpu.model}[/yellow]")
    console.print()

    # Driver
    console.print("[bold white]NVIDIA Driver[/bold white]")
    if report.driver.available and report.driver.version:
        console.print(f"  Version: [green]{report.driver.version}[/green]")
    else:
        console.print(f"  [yellow]{report.driver.status_message}[/yellow]")
    console.print()

    # OS
    console.print("[bold white]Operating System[/bold white]")
    console.print(f"  {report.os.name} ({report.os.architecture})")
    console.print()

    # Python
    console.print("[bold white]Python[/bold white]")
    console.print(f"  Version: {report.python.version}")
    console.print()

    if report.warnings:
        console.print("[bold yellow]Warnings / System Notes:[/bold yellow]")
        for w in report.warnings:
            console.print(f"  ⚠ {w}")
        console.print()


def print_plan(plan: InstallationPlan):
    print_section("Compatibility Analysis")

    if not plan.compatible:
        console.print("[bold red]❌ System incompatible or unsupported.[/bold red]")
        for err in plan.errors:
            console.print(f"  [red]• {err}[/red]")
        console.print()

    console.print("Backend:")
    console.print(f"  [cyan]{plan.backend}[/cyan]\n")

    console.print("Recommended ML framework:")
    console.print(f"  [cyan]{plan.framework}[/cyan]\n")

    console.print("Recommended Python:")
    console.print(f"  {plan.python_version}\n")

    console.print("Recommended PyTorch:")
    console.print(f"  {plan.framework_version}\n")

    if plan.cuda_runtime_version:
        console.print("Recommended CUDA runtime:")
        console.print(f"  {plan.cuda_runtime_version}\n")

    console.print("Environment:")
    console.print(f"  {plan.env_path}\n")

    console.print(DIVIDER)

    if plan.packages:
        console.print("[bold white]Packages to install:[/bold white]")
        for pkg in plan.packages:
            spec_str = f"{pkg.name}=={pkg.version}" if pkg.version else pkg.name
            console.print(f"  • {spec_str}")
        console.print()

    if plan.driver_requirement_status:
        console.print(f"[bold yellow]Driver Note:[/bold yellow] {plan.driver_requirement_status}\n")

    if plan.warnings:
        for w in plan.warnings:
            console.print(f"[bold yellow]⚠ Warning:[/bold yellow] {w}")
        console.print()


def print_verification(results: Dict[str, Any], env_path: str):
    print_section("Verification")

    all_passed = True
    for key, info in results.items():
        status = info.get("status", False)
        message = info.get("message", "")
        if status:
            console.print(f"{key:<20} [bold green]✓[/bold green] [dim]{message}[/dim]")
        else:
            all_passed = False
            console.print(f"{key:<20} [bold red]✗[/bold red] [red]{message}[/red]")

    console.print(f"{DIVIDER}\n")
    if all_passed:
        console.print("[bold green]HwPilot environment is ready.[/bold green]\n")
    else:
        console.print("[bold red]Verification completed with failures.[/bold red]\n")

    console.print("Environment:")
    console.print(f"  {env_path}\n")


def print_table_dict(title: str, data: Dict[str, Any]):
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Property", style="dim", width=25)
    table.add_column("Value")

    for k, v in data.items():
        table.add_row(str(k), str(v))

    console.print(table)
