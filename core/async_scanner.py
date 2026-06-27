"""
Async-based scanner using asyncio for true I/O parallelism
Replaces ThreadPoolExecutor to overcome GIL limitations
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from core.module_loader import ModuleLoader
from core.reporter import Reporter
from core.risk import RiskEngine
from core.url_parser import parse_target

logger = logging.getLogger(__name__)


class AsyncScanner:
    """Async scanner with efficient I/O-bound concurrency."""
    
    def __init__(self, max_concurrent=6):
        """
        Initialize async scanner.
        
        Args:
            max_concurrent: Max concurrent module tasks (default: 6)
        """
        self.loader = ModuleLoader()
        self.reporter = Reporter()
        self.risk = RiskEngine()
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def run(self, target: str = "localhost") -> Dict[str, Any]:
        """
        Run audit asynchronously.
        
        Args:
            target: Target hostname, IP, or domain
            
        Returns:
            Audit report dictionary
        """
        results = []
        modules = self.loader.load_modules()
        
        # Parse target once
        clean_target, parsed = parse_target(target)
        active_target = clean_target
        origin_ip_discovered = None
        
        logger.info(f"Starting async audit for: {target}")
        print(f"[*] Starting security audit for target: {target}")
        
        # Step 1: Run network module first (critical for origin detection)
        network_module = next(
            (m for m in modules if m.name == "Remote Connectivity & Origin IP Audit"),
            None
        )
        
        if network_module:
            print("[*] Running network analysis module...")
            try:
                # Call sync module in thread pool to avoid blocking
                net_result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: network_module.run(target=clean_target)
                )
                results.append(net_result)
                
                # Check for origin IP leaks
                if net_result.get("status") == "OK":
                    leaks = net_result.get("network_data", {}).get("subdomain_leaks_found", [])
                    if isinstance(leaks, list) and len(leaks) > 0:
                        origin_ip_discovered = leaks[0].get("ip")
                        print(
                            f"[🔥 WARNING] Origin IP leak detected via '{leaks[0].get('subdomain')}': {origin_ip_discovered}"
                        )
                        active_target = origin_ip_discovered
            except Exception as e:
                logger.error(f"Network module failed: {str(e)}")
                print(f"[!] Network module error: {str(e)}")
        
        # Step 2: Run remaining modules concurrently
        remaining_modules = [
            m for m in modules 
            if m.name != "Remote Connectivity & Origin IP Audit"
        ]
        
        print(f"[*] Running {len(remaining_modules)} audit modules concurrently...")
        
        # Create async tasks with semaphore
        tasks = [
            self._run_module_async(module, active_target)
            for module in remaining_modules
        ]
        
        # Wait for all tasks with proper error handling
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in batch_results:
            if isinstance(result, Exception):
                logger.error(f"Module task failed: {str(result)}")
                results.append({
                    "module": "UNKNOWN",
                    "status": "ERROR",
                    "details": str(result)
                })
            else:
                results.append(result)
        
        # Calculate overall risk
        risk = self.risk.calculate(results)
        
        # Build report
        report = {
            "target_requested": target,
            "target_executed": active_target,
            "origin_bypass_triggered": origin_ip_discovered is not None,
            "risk": risk,
            "results": results
        }
        
        self.reporter.write(report)
        print(f"[+] Audit complete. Risk level: {risk}")
        return report
    
    async def _run_module_async(self, module: Any, target: str) -> Dict[str, Any]:
        """
        Run module asynchronously with semaphore control.
        
        Args:
            module: Audit module to run
            target: Target to scan
            
        Returns:
            Module result dictionary
        """
        async with self.semaphore:
            try:
                # Run sync module in thread pool
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._run_module_safe(module, target)
                )
                return result
            except Exception as exc:
                logger.error(f"Module {getattr(module, 'name', 'UNKNOWN')} failed: {str(exc)}")
                return {
                    "module": getattr(module, "name", module.__class__.__name__),
                    "target": target,
                    "status": "ERROR",
                    "details": str(exc)
                }
    
    @staticmethod
    def _run_module_safe(module: Any, target: str) -> Dict[str, Any]:
        """
        Safely run a module with proper error handling.
        
        Args:
            module: Audit module
            target: Target hostname/IP
            
        Returns:
            Module result
        """
        try:
            try:
                result = module.run(target=target)
            except TypeError:
                result = module.run()
            
            if isinstance(result, dict):
                result["target"] = target
            
            return result
        except Exception as exc:
            logger.error(f"Module exception: {str(exc)}")
            return {
                "module": getattr(module, "name", module.__class__.__name__),
                "target": target,
                "status": "ERROR",
                "details": str(exc)
            }


def run_async_audit(target: str = "localhost", max_concurrent: int = 6) -> Dict[str, Any]:
    """
    Convenience function to run async audit.
    
    Args:
        target: Target to scan
        max_concurrent: Max concurrent modules
        
    Returns:
        Audit report
    """
    scanner = AsyncScanner(max_concurrent=max_concurrent)
    return asyncio.run(scanner.run(target))
