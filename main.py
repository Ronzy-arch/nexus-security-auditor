#!/usr/bin/env python3

import argparse

from core.version import VERSION
from core.module_loader import ModuleLoader
from core.scanner import Scanner


def cmd_audit(args):
    scanner = Scanner()
    report = scanner.run(target=args.target)

    print("\n=== Audit Completed ===")
    print(f"Target : {report.get('target', args.target)}")
    print(f"Risk   : {report.get('risk', 'UNKNOWN')}")
    print(f"Modules: {len(report.get('results', []))}")
    print("JSON   : reports/report.json")
    print("HTML   : reports/report.html")

def cmd_version(_):
    print(f"Nexus Security Auditor {VERSION}")
    print("Defensive Security Assessment Framework")
    print("License: MIT")


def cmd_list_modules(_):
    loader = ModuleLoader()
    for module in loader.list_modules():
        print(module)


def cmd_info(_):
    print("Nexus Security Auditor")
    print("Version:", VERSION)
    print("Framework: Defensive Security Assessment")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="nexus",
        description="Nexus Security Auditor"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit", help="Run security audit")
    audit.add_argument(
        "target",
        nargs="?",
        default="localhost",
        help="Target hostname, IP address, or domain (default: localhost)"
    )
    audit.set_defaults(func=cmd_audit)

    version = sub.add_parser("version", help="Show version")
    version.set_defaults(func=cmd_version)

    modules = sub.add_parser("list-modules", help="List available audit modules")
    modules.set_defaults(func=cmd_list_modules)

    info = sub.add_parser("info", help="Display project information")
    info.set_defaults(func=cmd_info)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
