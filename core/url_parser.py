"""
Single-pass URL/target parser to eliminate redundant parsing across modules
Centralizes target normalization for all audit operations
"""
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TargetParser:
    """Parse and normalize target URLs/hostnames once."""
    
    @staticmethod
    def parse(target: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse target into clean hostname and metadata.
        
        Args:
            target: Raw target (hostname, IP, URL)
            
        Returns:
            Tuple of (clean_hostname, metadata_dict)
            
        Example:
            >>> parse("https://example.com:8080/path")
            ('example.com', {'port': 8080, 'scheme': 'https', 'path': '/path'})
        """
        if not target:
            return "localhost", {"scheme": "http", "port": 80, "path": "/"}
        
        original = target
        metadata = {"scheme": "http", "port": 80, "path": "/"}
        
        # Extract scheme
        if "://" in target:
            scheme, target = target.split("://", 1)
            metadata["scheme"] = scheme.lower()
            metadata["port"] = 443 if scheme.lower() == "https" else 80
        
        # Extract path
        if "/" in target:
            target, path = target.split("/", 1)
            metadata["path"] = "/" + path
        
        # Extract port
        if ":" in target:
            host, port_str = target.rsplit(":", 1)
            try:
                metadata["port"] = int(port_str)
                target = host
            except ValueError:
                # Not a valid port, treat as part of hostname
                pass
        
        clean_hostname = target.strip().lower()
        
        logger.debug(f"Parsed target '{original}' -> '{clean_hostname}' with metadata {metadata}")
        return clean_hostname, metadata


def parse_target(target: str) -> Tuple[str, Dict[str, Any]]:
    """
    Convenience function to parse target.
    
    Args:
        target: Raw target string
        
    Returns:
        Tuple of (clean_hostname, metadata)
    """
    return TargetParser.parse(target)
