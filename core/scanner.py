from core.module_loader import ModuleLoader
from core.reporter import Reporter
from core.risk import RiskEngine


class Scanner:
    def __init__(self):
        self.loader = ModuleLoader()
        self.reporter = Reporter()
        self.risk = RiskEngine()

    def run(self, target="localhost"):
        results = []
        modules = self.loader.load_modules()
        
        # VARIABEL KONTROL: Menyimpan target asli saat ini
        active_target = target
        origin_ip_discovered = None

        print(f"[*] Memulai audit keamanan untuk target awal: {target}")

        # Langkah Pertama: Prioritaskan modul jaringan untuk mengendus kebocoran IP
        network_module = next((m for m in modules if m.name == "Remote Connectivity & Origin IP Audit"), None)
        if network_module:
            print("[*] Menjalankan modul analisis jaringan & intelijen IP asli...")
            try:
                net_result = network_module.run(target=target)
                results.append(net_result)
                
                # Periksa apakah ada IP internal asli yang bocor via subdomain
                if net_result.get("status") == "OK":
                    leaks = net_result.get("network_data", {}).get("subdomain_leaks_found", [])
                    if isinstance(leaks, list) and len(leaks) > 0:
                        # Mengambil IP bocor pertama sebagai target Server Origin asli
                        origin_ip_discovered = leaks[0].get("ip")
                        print(f"[🔥 WARNING] Kebocoran IP Asli Terdeteksi! Subdomain '{leaks[0].get('subdomain')}' menunjuk ke {origin_ip_discovered}")
                        print(f"[⚡ REDIRECT] Mengalihkan target pemindaian berikutnya langsung ke Server Internal: {origin_ip_discovered}")
                        active_target = origin_ip_discovered
            except Exception as e:
                print(f"[!] Gagal mengeksekusi modul jaringan awal: {str(e)}")

        # Langkah Kedua: Jalankan sisa modul lainnya menggunakan target aktif (yang mungkin sudah dialihkan)
        for module in modules:
            # Lewati modul jaringan karena sudah dieksekusi di awal
            if module.name == "Remote Connectivity & Origin IP Audit":
                continue

            try:
                # Eksekusi modul menggunakan target aktif (Domain atau IP Internal yang bocor)
                try:
                    result = module.run(target=active_target)
                except TypeError:
                    result = module.run()

                if isinstance(result, dict):
                    result["target"] = active_target

                results.append(result)

            except Exception as exc:
                results.append({
                    "module": getattr(module, "name", module.__class__.__name__),
                    "target": active_target,
                    "status": "ERROR",
                    "details": str(exc)
                })

        # Hitung tingkat risiko berdasarkan gabungan temuan
        risk = self.risk.calculate(results)

        # Jika terjadi pengalihan, tambahkan catatan khusus pada struktur laporan
        report = {
            "target_requested": target,
            "target_executed": active_target,
            "origin_bypass_triggered": True if origin_ip_discovered else False,
            "risk": risk,
            "results": results
        }

        self.reporter.write(report)
        print(f"[+] Pemindaian selesai. Hasil akhir dikompilasi dengan status risiko: {risk}")
        return report
