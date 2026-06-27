import socket
from core.base_module import BaseAuditModule


class ServiceAudit(BaseAuditModule):
    name = "Remote Port Scanner"

    def run(self, target="localhost"):
        # Daftar port umum: 21 (FTP), 22 (SSH), 23 (Telnet), 25 (SMTP), 53 (DNS), 80 (HTTP), 443 (HTTPS)
        ports_to_scan = (21, 22, 23, 25, 53, 80, 110, 139, 443, 445, 1433, 3306, 3389, 8080, 8443)
        open_services = []

        try:
            target_ip = socket.gethostbyname(target)
            
            for port in ports_to_scan:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.8)
                result = s.connect_ex((target_ip, port))
                
                if result == 0:
                    open_services.append({
                        "ip": target_ip,
                        "port": port,
                        "status": "OPEN"
                    })
                s.close()

            return {
                "module": self.name,
                "target": target,
                "status": "OK",
                "count": len(open_services),
                "services": open_services
            }

        except Exception as e:
            return {
                "module": self.name,
                "target": target,
                "status": "ERROR",
                "count": 0,
                "services": [],
                "details": str(e)
            }
