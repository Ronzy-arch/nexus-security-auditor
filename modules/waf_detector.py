import http.client
import urllib.parse
import random
from core.base_module import BaseAuditModule


class WafDetector(BaseAuditModule):
    name = "Advanced WAF & Firewall Detector"

    def run(self, target="localhost"):
        waf_detected = "None / Unresolved (Target terekspos langsung tanpa firewall publik)"
        confidence = "LOW"
        details = "Tidak ditemukan signature firewall populer pada header respons."

        if target in ["localhost", "127.0.0.1"]:
            return {
                "module": self.name,
                "target": target,
                "status": "OK",
                "waf_data": {
                    "firewall_type": "None (Localhost Development Environment)",
                    "confidence": "HIGH",
                    "details": "Sistem lokal berjalan tanpa lapisan proxy."
                }
            }

        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
        ]

        try:
            clean_target = target.replace("http://", "").replace("https://", "")
            if "/" in clean_target:
                clean_target = clean_target.split("/")

            provocation_payload = urllib.parse.quote("<script>alert('nexus_provoke');</script> SELECT * FROM users;")
            provoke_path = f"/?test={provocation_payload}"

            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": "text/html,application/xhtml+xml",
                "Connection": "close"
            }

            conn = http.client.HTTPConnection(clean_target, port=80, timeout=3.0)
            conn.request("GET", provoke_path, headers=headers)
            response = conn.getresponse()
            
            response_headers = {k.lower(): v.lower() for k, v in response.getheaders()}
            response_body = response.read().decode('utf-8', errors='ignore').lower()
            conn.close()
            
            if "server" in response_headers and "cloudflare" in response_headers["server"]:
                waf_detected = "Cloudflare Web Application Firewall"
                confidence = "HIGH"
                details = "Terdeteksi via header 'Server: cloudflare'."
            elif "__cfduid" in response_body or "cf-ray" in response_headers or "cf-mitigated" in response_headers:
                waf_detected = "Cloudflare Web Application Firewall"
                confidence = "HIGH"
                details = "Terdeteksi melalui ID pelacakan cookie atau header CF-RAY."

            elif "aws" in response_headers.get("x-amzn-requestid", "") or "awswaf" in response_headers.get("server", ""):
                waf_detected = "Amazon Web Services (AWS) WAF"
                confidence = "HIGH"
                details = "Terdeteksi melalui struktur tanda pengenal request X-Amzn."

            elif "mod_security" in response_headers.get("server", "") or "modsecurity" in response_body:
                waf_detected = "ModSecurity (OWASP CRS)"
                confidence = "HIGH"
                details = "Server secara terbuka membocorkan ekstensi ModSecurity di modul utama."

            elif "akamai" in response_headers.get("server", "") or "akavm" in response_headers:
                waf_detected = "Akamai Technologies Edge Defense"
                confidence = "HIGH"
                details = "Sidik jari ditemukan pada sistem penamaan server Akamai Edge."

            elif response.status in (403, 406, 499):
                waf_detected = "Generic / Custom Web Application Firewall"
                confidence = "MEDIUM"
                details = f"Paket provokasi diblokir dengan kode status HTTP {response.status}. Sistem keamanan aktif menolak input berbahaya."

            return {
                "module": self.name,
                "target": target,
                "status": "OK",
                "waf_data": {
                    "firewall_type": waf_detected,
                    "confidence": confidence,
                    "details": details
                }
            }

        except Exception as e:
            return {
                "module": self.name,
                "target": target,
                "status": "ERROR",
                "waf_data": {},
                "details": f"Gagal menganalisis firewall target: {str(e)}"
            }
