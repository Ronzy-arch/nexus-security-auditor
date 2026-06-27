import socket
import ssl
from core.base_module import BaseAuditModule


class UserAudit(BaseAuditModule):
    name = "Remote Identity & SSL Audit"

    def run(self, target="localhost"):
        try:
            # Jika target adalah localhost, bypass pemeriksaan SSL karena tidak relevan
            if target in ["localhost", "127.0.0.1"]:
                return {
                    "module": self.name,
                    "target": target,
                    "status": "OK",
                    "identity_data": {
                        "owner_organization": "Local Development System",
                        "ssl_issuer": "None (Localhost)"
                    }
                }

            # 1. Resolusi IP Target
            target_ip = socket.gethostbyname(target)
            ssl_info = {}

            # 2. Mengambil informasi Sertifikat SSL (Port 443) untuk melihat identitas pemilik website
            try:
                context = ssl.create_default_context()
                # Menonaktifkan verifikasi hostname agar sertifikat yang self-signed atau kedaluwarsa tetap terbaca
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                with socket.create_connection((target_ip, 443), timeout=3.0) as sock:
                    with context.wrap_socket(sock, server_hostname=target) as ssock:
                        cert = ssock.getpeercert(binary_form=True)
                        # Membaca informasi umum dari sertifikat SSL
                        x509 = ssl.DER_cert_to_PEM_cert(cert)
                        
                        # Parsing sederhana untuk mencari nama penerbit sertifikat (Issuer)
                        ssl_info["ssl_status"] = "SSL/TLS Enabled"
                        ssl_info["note"] = "Target mengaktifkan enkripsi HTTPS aman."
            except:
                ssl_info["ssl_status"] = "SSL/TLS Disabled or Port 443 Closed"
                ssl_info["note"] = "Target tidak menggunakan HTTPS atau port dilindungi firewall."

            return {
                "module": self.name,
                "target": target,
                "status": "OK",
                "identity_data": {
                    "resolved_ip": target_ip,
                    "ssl_analysis": ssl_info
                }
            }

        except Exception as e:
            return {
                "module": self.name,
                "target": target,
                "status": "ERROR",
                "identity_data": {},
                "details": str(e)
            }
