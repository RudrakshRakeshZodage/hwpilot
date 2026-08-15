"""Rich interactive console output formatting with clean aligned tables, panels, and badges for HwPilot CLI."""

import sys
import os
from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
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


def print_banner():
    """Prints the branded HwPilot banner."""
    console.print()
    console.print(
        Panel(
            "[bold cyan]⚡ HwPilot[/bold cyan] [bold white]— Hardware-Aware ML Environment Setup & Compatibility Manager[/bold white]\n"
            "[dim]Created by Rudraksh Rakesh Zodage • Zero-guesswork ML Environments[/dim]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 2),
        )
    )
    console.print()


def print_section(title: str):
    """Prints a styled section header."""
    console.print()
    console.print(f"[bold cyan]⚡ {title}[/bold cyan]")
    console.print("[dim]" + "─" * 60 + "[/dim]")
    console.print()


def print_detection_report(report: SystemReport):
    """Prints a clean, colorized Rich table of detected hardware and system specs without emoji misalignment."""
    print_banner()

    table = Table(
        title="[bold cyan]System Hardware & Environment Detection[/bold cyan]",
        title_justify="left",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold magenta",
        show_header=True,
        show_lines=False,
        padding=(0, 2),
    )

    table.add_column("Component", style="bold white", no_wrap=True)
    table.add_column("Detected Specification", style="white")
    table.add_column("Status", justify="center", no_wrap=True)

    # 1. CPU Row
    cpu_specs = (
        f"{report.cpu.model}\n"
        f"[dim]Architecture: {report.cpu.architecture} • Cores: {report.cpu.physical_cores} • Threads: {report.cpu.logical_cores}[/dim]"
    )
    if report.cpu.ram_gb > 0:
        cpu_specs += f"\n[dim]System RAM: {report.cpu.ram_gb:.1f} GB[/dim]"

    table.add_row(
        "CPU",
        cpu_specs,
        "[bold green]✓ Ready[/bold green]"
    )

    # 2. GPU Row
    if report.gpu.available:
        model_str = report.gpu.model
        vendor_str = report.gpu.vendor
        if model_str.lower().startswith(vendor_str.lower()):
            clean_gpu_name = model_str
        else:
            clean_gpu_name = f"{vendor_str} {model_str}"

        gpu_specs = f"[bold green]{clean_gpu_name}[/bold green]"
        if report.gpu.vram_gb > 0:
            gpu_specs += f"\n[dim]VRAM: {report.gpu.vram_gb:.1f} GB[/dim]"
        if report.gpu.compute_capability:
            gpu_specs += f" • [dim]Compute Capability: {report.gpu.compute_capability}[/dim]"

        gpu_status = "[bold green]✓ CUDA Acceleration[/bold green]" if vendor_str.lower() == "nvidia" else "[bold green]✓ GPU Active[/bold green]"
        table.add_row("GPU", gpu_specs, gpu_status)
    else:
        table.add_row("GPU", f"[yellow]{report.gpu.model}[/yellow]", "[yellow]CPU Mode Only[/yellow]")

    # 3. NVIDIA Driver Row
    if report.driver.available and report.driver.version:
        table.add_row(
            "NVIDIA Driver",
            f"Version [bold green]{report.driver.version}[/bold green]",
            "[bold green]✓ Supported[/bold green]"
        )
    else:
        table.add_row(
            "NVIDIA Driver",
            f"[dim]{report.driver.status_message}[/dim]",
            "[yellow]Not Found / CPU[/yellow]"
        )

    # 4. OS Row
    table.add_row(
        "Operating System",
        f"{report.os.name} ({report.os.architecture})",
        "[bold green]✓ Supported[/bold green]"
    )

    # 5. Python Runtime Row
    table.add_row(
        "Python Runtime",
        f"Python {report.python.version}",
        f"[bold green]✓ CPython {report.python.version_tuple[0]}.{report.python.version_tuple[1]}[/bold green]"
    )

    console.print(table)
    console.print()

    if report.warnings:
        console.print("[bold yellow]⚠ System Notes:[/bold yellow]")
        for w in report.warnings:
            console.print(f"  • [yellow]{w}[/yellow]")
        console.print()


def print_plan(plan: InstallationPlan):
    """Prints a sleek Rich table showing the resolved ML environment and package installation plan."""
    # 1. Compatibility Overview Table
    summary_table = Table(
        title="[bold green]Compatibility Resolution & Target Environment[/bold green]",
        title_justify="left",
        box=box.ROUNDED,
        border_style="green",
        header_style="bold cyan",
        show_header=True,
        show_lines=False,
        padding=(0, 2),
    )
    summary_table.add_column("Property", style="bold white", no_wrap=True)
    summary_table.add_column("Resolved Value", style="white")

    backend_badge = f"[bold green]{plan.backend}[/bold green] (NVIDIA CUDA Acceleration)" if plan.backend == "CUDA" else f"[bold yellow]{plan.backend}[/bold yellow]"
    summary_table.add_row("Compute Backend", backend_badge)
    summary_table.add_row("Target ML Framework", f"[bold magenta]{plan.framework} {plan.framework_version}[/bold magenta]")

    if plan.cuda_runtime_version:
        summary_table.add_row("CUDA Runtime Build", f"[bold cyan]CUDA {plan.cuda_runtime_version} (cu{plan.cuda_runtime_version.replace('.', '')})[/bold cyan]")

    summary_table.add_row("Python Runtime", f"Python {plan.python_version}")
    summary_table.add_row("Target Environment", f"[bold yellow]{plan.env_path}[/bold yellow]")

    if plan.index_url:
        summary_table.add_row("PyTorch Wheel Index", f"[dim]{plan.index_url}[/dim]")

    console.print(summary_table)
    console.print()

    # 2. Packages Table
    if plan.packages:
        pkg_table = Table(
            title="[bold cyan]Resolved Packages to Install[/bold cyan]",
            title_justify="left",
            box=box.ROUNDED,
            border_style="cyan",
            header_style="bold magenta",
            show_header=True,
            show_lines=False,
            padding=(0, 2),
        )
        pkg_table.add_column("Package Name", style="bold white", no_wrap=True)
        pkg_table.add_column("Version Spec", style="bold green", no_wrap=True)
        pkg_table.add_column("Distribution Channel", style="dim")
        pkg_table.add_column("Estimated Size", justify="right", no_wrap=True)

        for pkg in plan.packages:
            ver = f"=={pkg.version}" if pkg.version else "Latest Matching"
            if pkg.name == "torch":
                est_size = "~2.53 GB"
                channel = "PyTorch CUDA Wheel Index"
            elif pkg.name == "torchvision":
                est_size = "~6.1 MB"
                channel = "PyTorch CUDA Wheel Index"
            elif pkg.name == "torchaudio":
                est_size = "~328 kB"
                channel = "PyTorch CUDA Wheel Index"
            else:
                est_size = "—"
                channel = "PyPI Simple"

            pkg_table.add_row(f"• {pkg.name}", ver, channel, est_size)

        console.print(pkg_table)
        console.print()

    if plan.driver_requirement_status:
        console.print(f"[bold yellow]Driver Note:[/bold yellow] {plan.driver_requirement_status}\n")

    if plan.warnings:
        for w in plan.warnings:
            console.print(f"[bold yellow]⚠ Warning:[/bold yellow] {w}")
        console.print()


def print_verification(results: Dict[str, Any], env_path: str):
    """Prints verification results in a beautiful Rich Table and activation instructions in a Panel."""
    verif_table = Table(
        title="[bold green]Environment Runtime Verification Results[/bold green]",
        title_justify="left",
        box=box.ROUNDED,
        border_style="green",
        header_style="bold cyan",
        show_header=True,
        show_lines=False,
        padding=(0, 2),
    )
    verif_table.add_column("Verification Step", style="bold white", no_wrap=True)
    verif_table.add_column("Status", justify="center", no_wrap=True)
    verif_table.add_column("Runtime Output Details", style="dim white")

    all_passed = True
    for key, info in results.items():
        status = info.get("status", False)
        message = info.get("message", "")
        if status:
            status_badge = "[bold green]✓ PASSED[/bold green]"
            verif_table.add_row(key, status_badge, f"[green]{message}[/green]")
        else:
            all_passed = False
            status_badge = "[bold red]✗ FAILED[/bold red]"
            verif_table.add_row(key, status_badge, f"[red]{message}[/red]")

    console.print(verif_table)
    console.print()

    if all_passed:
        act_cmd = f"{env_path}\\Scripts\\activate" if sys.platform == "win32" else f"source {env_path}/bin/activate"
        verify_cmd = f"hwpilot verify --path {env_path}"

        panel_content = (
            f"[bold green]🎉 All hardware and GPU verification checks passed successfully![/bold green]\n\n"
            f"[bold white]1. Activate your environment:[/bold white]\n"
            f"   [bold yellow]{act_cmd}[/bold yellow]\n\n"
            f"[bold white]2. Re-verify anytime:[/bold white]\n"
            f"   [bold cyan]{verify_cmd}[/bold cyan]\n\n"
            f"[dim]Environment manifest saved to: {env_path}\\manifest.json[/dim]"
        )

        console.print(
            Panel(
                panel_content,
                title="[bold green]✨ HwPilot Environment Ready[/bold green]",
                border_style="green",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
    else:
        console.print(
            Panel(
                "[bold red]❌ Verification completed with issues. Please review the errors above.[/bold red]",
                border_style="red",
                box=box.ROUNDED,
            )
        )
    console.print()


def print_table_dict(title: str, data: Dict[str, Any]):
    table = Table(title=title, show_header=True, header_style="bold magenta", box=box.ROUNDED, padding=(0, 2))
    table.add_column("Property", style="bold white", no_wrap=True)
    table.add_column("Value", style="cyan")

    for k, v in data.items():
        table.add_row(str(k), str(v))

    console.print(table)
