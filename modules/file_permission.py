import http.client
import urllib.parse
from core.base_module import BaseAuditModule


class FilePermissionAudit(BaseAuditModule):
    name = "Remote Security Headers Audit"

    def run(self, target="localhost"):
        results = []

        # Daftar header keamanan penting yang wajib ada di server web modern
        security_headers = {
            "Strict-Transport-Security": "Mencegah koneksi HTTP tidak aman (MitM).",
            "Content-Security-Policy": "Mencegah serangan injeksi data dan XSS.",
            "X-Frame-Options": "Mencegah serangan manipulasi klik (Clickjacking).",
            "X-Content-Type-Options": "Mencegah eksploitasi salah tipe file (MIME sniffing).",
            "Referrer-Policy": "Melindungi informasi data rujukan (referrer data)."
        }

        try:
            # Membersihkan target dan memastikan formatnya murni string HOSTNAME / IP
            clean_target = target.replace("http://", "").replace("https://", "")
            if "/" in clean_target:
                clean_target = clean_target.split("/")[0]

            # Melakukan koneksi HTTP dasar untuk mengambil header respons server
            conn = http.client.HTTPConnection(clean_target, port=80, timeout=2.0)
            conn.request("GET", "/")
            response = conn.getresponse()
            
            # Mengambil semua nama header yang dikirim oleh server target (diubah ke huruf kecil)
            target_headers = {k.lower(): v for k, v in response.getheaders()}
            conn.close()

            for header, desc in security_headers.items():
                header_lower = header.lower()
                
                if header_lower in target_headers:
                    results.append({
                        "header": header,
                        "status": "CONFIGURED",
                        "value": target_headers[header_lower],
                        "info": desc
                    })
                else:
                    results.append({
                        "header": header,
                        "status": "MISSING",
                        "value": "NOT_FOUND",
                        "info": f"⚠️ Berisiko! {desc}"
                    })

            return {
                "module": self.name,
                "target": target,
                "status": "OK",
                "results": results
            }

        except Exception as e:
            return {
                "module": self.name,
                "target": target,
                "status": "ERROR",
                "results": [],
                "details": f"Gagal mengambil header dari target jarak jauh: {str(e)}"
            }
