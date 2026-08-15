"""Main CLI interface for HwPilot."""

import sys
import json
import argparse
from pathlib import Path

from hwpilot import __version__
from hwpilot.detector import detect_system
from hwpilot.resolver import resolve_environment
from hwpilot.installer import create_environment, get_venv_python, install_plan
from hwpilot.verifier import verify_environment
from hwpilot.environment import create_persistent_manifest
from hwpilot.metadata import update_metadata, load_metadata
from hwpilot.utils import (
    print_banner,
    print_section,
    print_plan,
    print_verification,
    print_detection_report,
    setup_logger,
)


def cmd_detect(args):
    report = detect_system()
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print_detection_report(report)


def cmd_check(args):
    report = detect_system()
    plan = resolve_environment(
        report,
        env_path=args.path,
        is_global=args.global_env,
        req_pytorch_version=args.pytorch_ver,
        req_cuda_version=args.cuda_ver,
    )

    suitable = plan.compatible and (report.cpu.logical_cores >= 2)
    reasons = []

    if not plan.compatible:
        reasons.extend(plan.errors)
    if report.cpu.logical_cores < 2:
        reasons.append("Low CPU core count (< 2 logical cores).")
    if not report.gpu.available:
        reasons.append("No dedicated hardware GPU detected (CPU mode fallback).")
    if report.driver.vendor == "NVIDIA" and not report.driver.available:
        reasons.append("NVIDIA driver unavailable or nvidia-smi missing.")

    output = {
        "suitable": suitable,
        "backend": plan.backend,
        "framework": plan.framework,
        "reasons": reasons,
        "system": report.to_dict(),
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print_banner()
        print_section("Machine ML Suitability Check")
        if suitable:
            print("Status: [bold green]SUITABLE FOR ML WORKLOADS[/bold green]\n")
            print(f"Backend: {plan.backend}")
            print(f"Recommended Framework: {plan.framework} v{plan.framework_version}\n")
        else:
            print("Status: [bold yellow]LIMITED OR INCOMPATIBLE FOR ACCELERATED ML[/bold yellow]\n")

        if reasons:
            print("Notes / Reasons:")
            for r in reasons:
                print(f"  • {r}")
            print()


def cmd_plan(args):
    report = detect_system()
    plan = resolve_environment(
        report,
        env_path=args.path,
        is_global=args.global_env,
        req_pytorch_version=args.pytorch_ver,
        req_cuda_version=args.cuda_ver,
    )

    if args.json:
        out = {
            "system": report.to_dict(),
            "plan": plan.to_dict(),
        }
        print(json.dumps(out, indent=2))
    else:
        print_banner()
        print_plan(plan)


def cmd_setup(args):
    logger = setup_logger(verbose=args.verbose)

    # 1. Detect
    report = detect_system()

    # 2. Plan
    plan = resolve_environment(
        report,
        env_path=args.path,
        is_global=args.global_env,
        req_pytorch_version=args.pytorch_ver,
        req_cuda_version=args.cuda_ver,
    )

    if args.json:
        # JSON plan setup preview
        print(json.dumps({"status": "plan_ready", "plan": plan.to_dict()}, indent=2))
        if not args.yes:
            sys.exit(0)

    else:
        print_banner()
        print_plan(plan)

        if not plan.compatible:
            print("\n❌ Environment setup aborted due to compatibility errors.")
            sys.exit(1)

        if args.global_env:
            print("⚠ WARNING: You selected --global. Packages will be installed directly into current Python.")

        print("Installation plan ready.\n")

        if not args.yes:
            confirm = input("Proceed with installation? [Y/n] ").strip().lower()
            if confirm and confirm not in ("y", "yes"):
                print("Setup cancelled by user.")
                sys.exit(0)

    # 3. Create Environment
    if not args.global_env:
        print(f"\nCreating virtual environment at [cyan]{plan.env_path}[/cyan]...")
        success, msg, python_exe = create_environment(plan.env_path)
        print(f"  {msg}")
        if not success:
            print(f"\n❌ Environment creation failed: {msg}")
            sys.exit(1)
    else:
        python_exe = Path(sys.executable)

    # 4. Install Packages
    print("\nInstalling resolved ML packages (this may take a few minutes)...")
    installed_ok, status_msg, install_logs = install_plan(plan, python_exe)
    if not installed_ok:
        print(f"\n❌ Package installation failed: {status_msg}")
        sys.exit(1)
    print("  ✓ Package installation complete.")

    # 5. Verification
    print("\nExecuting runtime verification tests...")
    all_verified, verification_results = verify_environment(python_exe)

    if not args.json:
        print_verification(verification_results, plan.env_path)

    # 6. Persistent Manifest
    manifest_path = create_persistent_manifest(
        plan.env_path, report, plan, verification_results, install_logs
    )
    print(f"Environment manifest saved to: [dim]{manifest_path}[/dim]\n")


def cmd_verify(args):
    env_path = Path(args.path).resolve()
    python_exe = get_venv_python(env_path) if not args.global_env else Path(sys.executable)

    all_passed, results = verify_environment(python_exe)

    if args.json:
        out = {
            "env_path": str(env_path),
            "verified": all_passed,
            "results": results,
        }
        print(json.dumps(out, indent=2))
    else:
        print_banner()
        print_verification(results, str(env_path))


def cmd_doctor(args):
    setup_logger(verbose=True)
    report = detect_system()
    plan = resolve_environment(
        report,
        env_path=args.path,
        is_global=args.global_env,
        req_pytorch_version=args.pytorch_ver,
        req_cuda_version=args.cuda_ver,
    )

    doc_data = {
        "hwpilot_version": __version__,
        "python_executable": sys.executable,
        "system_report": report.to_dict(),
        "resolved_plan": plan.to_dict(),
    }

    if args.json:
        print(json.dumps(doc_data, indent=2))
    else:
        print_banner()
        print_section("HwPilot Doctor Diagnostics")
        print(f"HwPilot Version: {__version__}")
        print(f"Python Executable: {sys.executable}\n")

        print("Hardware Summary:")
        print(f"  CPU: {report.cpu.vendor} {report.cpu.model} ({report.cpu.logical_cores} cores)")
        print(f"  GPU: {report.gpu.vendor} {report.gpu.model} (VRAM: {report.gpu.vram_gb} GB)")
        print(f"  Driver: {report.driver.status_message}")
        print(f"  OS: {report.os.name}\n")

        print("Compatibility Diagnosis:")
        print(f"  Backend: {plan.backend}")
        print(f"  Framework: {plan.framework} v{plan.framework_version}")
        print(f"  Compatible: {'Yes' if plan.compatible else 'No'}\n")

        if plan.warnings or plan.errors:
            print("Diagnostics / Warnings:")
            for w in plan.warnings:
                print(f"  ⚠ {w}")
            for e in plan.errors:
                print(f"  ❌ {e}")
            print()


def cmd_info(args):
    meta = load_metadata()
    info_data = {
        "name": "HwPilot",
        "tagline": "Hardware-aware ML environment setup and compatibility manager.",
        "version": __version__,
        "author": "Rudraksh Rakesh Zodage",
        "email": "rudrakshrakeshzodage@gmail.com",
        "github": "https://github.com/RudrakshRakeshZodage/hwpilot",
        "linkedin": "https://www.linkedin.com/in/rudraksh-zodage-/",
        "huggingface": "https://huggingface.co/rudrakshrakeshzodage",
        "metadata_version": meta.get("version", "unknown"),
        "metadata_updated_at": meta.get("updated_at", "unknown"),
    }

    if args.json:
        print(json.dumps(info_data, indent=2))
    else:
        print_banner()
        print(f"[bold white]Tagline:[/bold white] {info_data['tagline']}")
        print(f"[bold white]Version:[/bold white] v{info_data['version']}")
        print(f"[bold white]Author:[/bold white] {info_data['author']} ({info_data['email']})")
        print(f"[bold white]GitHub:[/bold white] {info_data['github']}")
        print(f"[bold white]LinkedIn:[/bold white] {info_data['linkedin']}")
        print(f"[bold white]HuggingFace:[/bold white] {info_data['huggingface']}")
        print(f"[bold white]Metadata Version:[/bold white] {info_data['metadata_version']}")
        print(f"[bold white]Metadata Updated:[/bold white] {info_data['metadata_updated_at']}\n")


def cmd_update(args):
    print_banner()
    print("Updating compatibility metadata cache...")
    ok, msg, data = update_metadata()
    if args.json:
        print(json.dumps({"success": ok, "message": msg, "version": data.get("version")}, indent=2))
    else:
        if ok:
            print(f"[bold green]✓ {msg}[/bold green]")
        else:
            print(f"[bold yellow]⚠ {msg}[/bold yellow]")
        print(f"Active Metadata Version: {data.get('version', '1.0.0')}\n")


def main():
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON format.")
    common_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    common_parser.add_argument(
        "--path", "-p", default="./hwpilot-env", help="Target virtual environment directory (default: ./hwpilot-env)."
    )
    common_parser.add_argument("--global", dest="global_env", action="store_true", help="Use current global Python environment.")
    common_parser.add_argument("--pytorch", "--torch", dest="pytorch_ver", help="Suggest specific PyTorch version (e.g. 2.4.1, 2.3.1).")
    common_parser.add_argument("--cuda", dest="cuda_ver", help="Suggest specific CUDA version (e.g. 12.4, 12.1, 11.8, cpu).")

    parser = argparse.ArgumentParser(
        prog="hwpilot",
        description="HwPilot — Hardware-aware ML environment setup and compatibility manager.",
        parents=[common_parser],
    )
    parser.add_argument("--version", action="version", version=f"hwpilot {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="HwPilot subcommands")

    # detect
    p_detect = subparsers.add_parser("detect", parents=[common_parser], help="Inspect hardware and system environment.")
    p_detect.set_defaults(func=cmd_detect)

    # check
    p_check = subparsers.add_parser("check", parents=[common_parser], help="Determine if current machine is suitable for ML workloads.")
    p_check.set_defaults(func=cmd_check)

    # plan
    p_plan = subparsers.add_parser("plan", parents=[common_parser], help="Create installation plan without modifying system.")
    p_plan.set_defaults(func=cmd_plan)

    # setup
    p_setup = subparsers.add_parser("setup", parents=[common_parser], help="Full workflow: detect, resolve, confirm, install & verify.")
    p_setup.add_argument("-y", "--yes", action="store_true", help="Bypass interactive confirmation prompt.")
    p_setup.set_defaults(func=cmd_setup)

    # verify
    p_verify = subparsers.add_parser("verify", parents=[common_parser], help="Verify runtime capability of an existing environment.")
    p_verify.set_defaults(func=cmd_verify)

    # doctor
    p_doctor = subparsers.add_parser("doctor", parents=[common_parser], help="Run comprehensive diagnostics on environment and hardware.")
    p_doctor.set_defaults(func=cmd_doctor)

    # info
    p_info = subparsers.add_parser("info", parents=[common_parser], help="Display HwPilot package and metadata information.")
    p_info.set_defaults(func=cmd_info)

    # update
    p_update = subparsers.add_parser("update", parents=[common_parser], help="Refresh cached package compatibility metadata.")
    p_update.set_defaults(func=cmd_update)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Execute subcommand
    args.func(args)


if __name__ == "__main__":
    main()
