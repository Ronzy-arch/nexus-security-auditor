import socket
from core.base_module import BaseAuditModule


class SystemAudit(BaseAuditModule):
    name = "Remote OS & Banner Grabber"

    def run(self, target="localhost"):
        detected_banners = {}

        try:
            target_ip = socket.gethostbyname(target)
            ports_to_check = (22, 80)
            
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.5)
                s.connect((target_ip, 22))
                ssh_banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
                detected_banners["ssh_banner"] = ssh_banner
                s.close()
            except:
                pass

            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.5)
                s.connect((target_ip, 80))
                s.sendall(b"HEAD / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
                http_response = s.recv(1024).decode('utf-8', errors='ignore')
                s.close()

                for line in http_response.split("\r\n"):
                    if line.lower().startswith("server:"):
                        detected_banners["web_server"] = line.split(":", 1)[1].strip()
            except:
                pass

        except Exception as e:
            return {
                "module": self.name,
                "target": target,
                "status": "ERROR",
                "data": {},
                "details": str(e)
            }

        return {
            "module": self.name,
            "target": target,
            "status": "OK",
            "data": {
                "resolved_ip": target_ip,
                "fingerprints": detected_banners if detected_banners else "No public banners exposed"
            }
        }
