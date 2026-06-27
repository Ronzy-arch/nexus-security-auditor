#!/usr/bin/env python3

import argparse
import logging
import sys

from core.version import VERSION
from core.module_loader import ModuleLoader
from core.scanner import Scanner
from core.http_pool import close_http_pool
from core.dns_cache import get_dns_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/nexus.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def cmd_audit(args):
    """Run security audit dengan optimisasi performa"""
    try:
        logger.info(f"Starting audit on target: {args.target}")
        scanner = Scanner(max_workers=6)  # Parallelisasi dengan 6 worker threads
        report = scanner.run(target=args.target)

        print("\n=== Audit Completed ===")
        print(f"Target : {report.get('target', args.target)}")
        print(f"Risk   : {report.get('risk', 'UNKNOWN')}")
        print(f"Modules: {len(report.get('results', []))}")
        print("JSON   : reports/report.json")
        print("HTML   : reports/report.html")
        
        # Print DNS cache stats
        dns_cache = get_dns_cache()
        dns_stats = dns_cache.stats()
        print(f"\nDNS Cache Stats:")
        print(f"  Size: {dns_stats['size']} entries")
        print(f"  Hit Rate: {dns_stats['hit_rate']}")
        print(f"  Total Queries: {dns_stats['total_queries']}")
        
    except Exception as e:
        logger.error(f"Audit failed: {str(e)}")
        print(f"[!] Audit gagal: {str(e)}")
        sys.exit(1)
    finally:
        # Cleanup resources
        close_http_pool()


def cmd_version(_):
    print(f"Nexus Security Auditor {VERSION}")
    print("Defensive Security Assessment Framework")
    print("License: MIT")
    print("\nPerformance Optimizations:")
    print("  - ThreadPoolExecutor untuk parallelisasi modul audit (6 workers)")
    print("  - HTTP Connection Pool dengan reuse koneksi")
    print("  - DNS Resolution Cache dengan TTL 300s")
    print("  - Retry Handler dengan exponential backoff")
    print("  - Response streaming dengan limit 500KB-1MB")


def cmd_list_modules(_):
    loader = ModuleLoader()
    modules = loader.list_modules()
    print(f"Available Audit Modules ({len(modules)}):")
    for i, module in enumerate(modules, 1):
        print(f"  {i}. {module}")


def cmd_info(_):
    print("Nexus Security Auditor")
    print(f"Version: {VERSION}")
    print("Framework: Defensive Security Assessment")
    print("\nFeatures:")
    print("  - Modular audit framework dengan plugin architecture")
    print("  - OWASP-aligned security checks")
    print("  - Extensible audit modules")
    print("  - Structured JSON & HTML reporting")
    print("  - CLI interface")
    print("\nPerformance Features:")
    print("  - Parallel module execution (6 concurrent workers)")
    print("  - HTTP connection pooling dan reuse")
    print("  - DNS caching dengan automatic TTL management")
    print("  - Adaptive retry logic dengan exponential backoff")
    print("  - Memory-efficient response streaming")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="nexus",
        description="Nexus Security Auditor - Defensive Security Assessment Framework"
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
