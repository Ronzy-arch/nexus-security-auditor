class RiskEngine:
    def calculate(self, results):
        high_count = 0
        medium_count = 0
        
        for result in results:
            if not isinstance(result, dict) or result.get("status") != "OK":
                continue
                
            # 1. Memeriksa temuan celah dari modul 'Remote Vulnerability Analyzer'
            vulns = result.get("vulnerabilities_found", [])
            if isinstance(vulns, list):
                for v in vulns:
                    if v.get("risk_level") == "HIGH":
                        high_count += 1
                    elif v.get("risk_level") == "MEDIUM":
                        medium_count += 1

            # 2. INTEGRASI BARU: Memeriksa temuan celah dari 'Remote Web App Vulnerability Scanner'
            if result.get("module") == "Remote Web App Vulnerability Scanner":
                # Jika status kembalian bukan string 'Safe...', berarti ada kerentanan riil ditemukan
                web_vulns = result.get("vulnerabilities_found", [])
                if isinstance(web_vulns, list):
                    for wv in web_vulns:
                        if wv.get("severity") == "HIGH":
                            high_count += 1
                        elif wv.get("severity") == "MEDIUM":
                            medium_count += 1
                        
            # 3. Memeriksa kebocoran file sensitif dari modul File System
            exposed_files = result.get("exposed_web_files", [])
            if isinstance(exposed_files, list):
                for f in exposed_files:
                    if f.get("severity") == "HIGH":
                        high_count += 1
                    elif f.get("severity") == "MEDIUM":
                        medium_count += 1

        # MENENTUKAN SKOR AKHIR DAN INDIKATOR BAHAYA
        if high_count > 0:
            return f"HIGH RISK ({high_count} Celah Keamanan Kritis Terdeteksi!)"
        elif medium_count > 0:
            return f"MEDIUM RISK ({medium_count} Indikasi Kerentanan Butuh Perbaikan)"
        else:
            return "LOW RISK / SAFE (Sistem Terkonfigurasi dengan Cukup Baik)"
