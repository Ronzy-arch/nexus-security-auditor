import socket
import http.client
from core.base_module import BaseAuditModule


class PasswordPolicyAudit(BaseAuditModule):
    name = "Remote Authentication Endpoint Audit"

    def run(self, target="localhost"):
        exposed_auth_endpoints = []

        try:
            target_ip = socket.gethostbyname(target)
            clean_target = target.replace("http://", "").replace("https://", "").split("/")

            # 1. Periksa apakah Port SSH (22) terbuka (Target utama brute force kata sandi)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.0)
                if s.connect_ex((target_ip, 22)) == 0:
                    exposed_auth_endpoints.append({
                        "type": "Network Service",
                        "name": "SSH (Port 22)",
                        "risk": "MEDIUM",
                        "description": "Pintu masuk remote login aktif. Pastikan menggunakan autentikasi SSH Key, bukan password."
                    })
                s.close()
            except:
                pass

            # 2. Periksa halaman login web yang umum terekspos ke publik
            login_paths = [
                "/login",
                "/admin/login",
                "/wp-login.php",
                "/user/login"
            ]

            for path in login_paths:
                try:
                    conn = http.client.HTTPConnection(clean_target, port=80, timeout=1.0)
                    conn.request("HEAD", path)
                    response = conn.getresponse()
                    
                    # Status 200 (OK) menandakan halaman login tersebut eksis
                    if response.status == 200:
                        exposed_auth_endpoints.append({
                            "type": "Web Page",
                            "name": path,
                            "risk": "LOW",
                            "description": "Halaman login web terdeteksi publik. Rentan serangan brute force jika tidak dilindungi Captcha/Rate Limiting."
                        })
                    conn.close()
                except:
                    continue

            return {
                "module": self.name,
                "target": target,
                "status": "OK",
                "count": len(exposed_auth_endpoints),
                "results": exposed_auth_endpoints if exposed_auth_endpoints else "Secure (No common public auth interfaces discovered)"
            }

        except Exception as e:
            return {
                "module": self.name,
                "target": target,
                "status": "ERROR",
                "results": [],
                "details": str(e)
            }
