import socket
from core.base_module import BaseAuditModule


class PatchAudit(BaseAuditModule):
    name = "Remote Web Patch & Software Audit"

    def run(self, target="localhost"):
        software_detected = []

        try:
            target_ip = socket.gethostbyname(target)
            
            # Melakukan koneksi HTTP dasar ke port 80 untuk membaca banner aplikasi
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2.0)
                s.connect((target_ip, 80))
                s.sendall(b"HEAD / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
                response = s.recv(1024).decode('utf-8', errors='ignore')
                s.close()

                # Mencari baris "Server:" untuk mengekstrak versi perangkat lunak target
                for line in response.split("\r\n"):
                    if line.lower().startswith("server:"):
                        server_header = line.split(":", 1)[1].strip()
                        
                        # Analisis dasar patch/pembaruan berdasarkan informasi banner yang bocor
                        patch_status = "UNKNOWN (Version hidden or secure)"
                        risk = "LOW"
                        advice = "Konfigurasi server sudah baik jika menyembunyikan detail versi."
                        
                        # Contoh analisis jika server membocorkan versi lama yang spesifik
                        if any(char.isdigit() for char in server_header):
                            patch_status = "POTENTIALLY OUTDATED"
                            risk = "MEDIUM"
                            advice = "Server membocorkan nomor versi spesifik. Segera sembunyikan banner server atau lakukan patch ke versi terbaru untuk mencegah exploitasi otomatis."

                        software_detected.append({
                            "component": "Web Server",
                            "banner": server_header,
                            "patch_status": patch_status,
                            "risk_level": risk,
                            "remediation": advice
                        })
            except:
                pass

            return {
                "module": self.name,
                "target": target,
                "status": "OK",
                "count": len(software_detected),
                "results": software_detected if software_detected else "Secure (No public software versions exposed)"
            }

        except Exception as e:
            return {
                "module": self.name,
                "target": target,
                "status": "ERROR",
                "results": [],
                "details": str(e)
            }
