import socket
import subprocess
import platform
from core.base_module import BaseAuditModule
from core.dns_cache import get_dns_cache
import logging

logger = logging.getLogger(__name__)


class NetworkAudit(BaseAuditModule):
    name = "Remote Connectivity & Origin IP Audit"

    def run(self, target="localhost"):
        try:
            dns_cache = get_dns_cache()
            
            # 1. Resolusi IP Utama dengan cache
            target_ip = dns_cache.resolve(target)
            if not target_ip:
                target_ip = socket.gethostbyname(target)
            
            # Daftar subdomain yang sering melewatkan konfigurasi WAF/Proxy
            common_subdomains = ("mail", "ftp", "dev", "staging", "cpanel", "direct", "admin", "test")
            origin_ip_leads = []

            # Membersihkan nama domain utama untuk kebutuhan pencarian subdomain
            clean_domain = target.replace("http://", "").replace("https://", "").split("/")[0]
            
            # Jika target bukan localhost, lakukan pencarian kebocoran subdomain
            if target not in ("localhost", "127.0.0.1"):
                for sub in common_subdomains:
                    subdomain_full = f"{sub}.{clean_domain}"
                    try:
                        # Gunakan DNS cache untuk resolution
                        sub_ip = dns_cache.resolve(subdomain_full)
                        if sub_ip is None:
                            # Fallback jika cache gagal
                            sub_ip = socket.gethostbyname(subdomain_full)
                        
                        # Jika IP subdomain berbeda dengan IP utama, ada kemungkinan itu IP internal asli
                        if sub_ip != target_ip and sub_ip not in [item["ip"] for item in origin_ip_leads]:
                            origin_ip_leads.append({
                                "subdomain": subdomain_full,
                                "ip": sub_ip,
                                "status": "POTENTIAL_ORIGIN_LEAK"
                            })
                    except (socket.gaierror, Exception):
                        continue

            # 2. Network Ping untuk verifikasi keaktifan host utama
            param = "-n" if platform.system().lower() == "windows" else "-c"
            command = ["ping", param, "1", target_ip]
            try:
                ping_run = subprocess.run(
                    command, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    timeout=2.5
                )
                host_status = "ALIVE / ONLINE" if ping_run.returncode == 0 else "UNREACHABLE / FILTERED"
            except Exception as ping_error:
                logger.warning(f"Ping failed: {str(ping_error)}")
                host_status = "PING_UNAVAILABLE"

            return {
                "module": self.name,
                "target": target,
                "status": "OK",
                "network_data": {
                    "resolved_ip": target_ip,
                    "host_status": host_status,
                    "subdomain_leaks_found": origin_ip_leads if origin_ip_leads else "Clean (No simple origin IP leaks via subdomains)"
                }
            }

        except Exception as e:
            logger.error(f"Network audit error: {str(e)}")
            return {
                "module": self.name,
                "target": target,
                "status": "ERROR",
                "network_data": {},
                "details": str(e)
            }
