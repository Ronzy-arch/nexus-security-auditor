import socket
from core.base_module import BaseAuditModule


class ProcessAudit(BaseAuditModule):
    name = "Remote Vulnerability Analyzer"

    def run(self, target="localhost"):
        vulnerabilities = []
        risky_ports = {
            21: {"service": "FTP", "risk": "MEDIUM", "desc": "Rentan penyadapan teks polos & Brute Force."},
            23: {"service": "Telnet", "risk": "HIGH", "desc": "Protokol usang tanpa enkripsi. Sangat berbahaya!"},
            445: {"service": "SMB", "risk": "HIGH", "desc": "Rentan eksploitasi Remote Code Execution (misal: EternalBlue)."},
            3389: {"service": "RDP", "risk": "HIGH", "desc": "Akses Remote Desktop terbuka, target utama Ransomware."}
        }

        try:
            target_ip = socket.gethostbyname(target)
            
            for port, info in risky_ports.items():
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.8)
                result = s.connect_ex((target_ip, port))
                
                if result == 0:
                    vulnerabilities.append({
                        "port": port,
                        "service": info["service"],
                        "risk_level": info["risk"],
                        "description": info["desc"]
                    })
                s.close()

            return {
                "module": self.name,
                "target": target,
                "status": "OK",
                "count": len(vulnerabilities),
                "vulnerabilities_found": vulnerabilities if vulnerabilities else "Safe (No high-risk public ports exposed)"
            }

        except Exception as e:
            return {
                "module": self.name,
                "target": target,
                "status": "ERROR",
                "vulnerabilities_found": [],
                "details": str(e)
            }
