import http.client
from core.base_module import BaseAuditModule


class FilesystemAudit(BaseAuditModule):
    name = "Remote Web Filesystem & Path Audit"

    def run(self, target="localhost"):
        exposed_paths = []
        
        # Daftar file/folder sensitif yang sering bocor di server web
        paths_to_check = [
            "/.env",
            "/config.json",
            "/.git/HEAD",
            "/backup.zip",
            "/wp-config.php",
            "/admin/",
            "/robots.txt"
        ]

        try:
            # Jika target berupa IP atau tidak mengandung skema, bersihkan untuk koneksi HTTP
            clean_target = target.replace("http://", "").replace("https://", "").split("/")[0]

            for path in paths_to_check:
                try:
                    # Melakukan koneksi HTTP dasar ke port 80 target
                    conn = http.client.HTTPConnection(clean_target, port=80, timeout=1.5)
                    conn.request("HEAD", path)
                    response = conn.getresponse()
                    
                    # Status 200 (OK) atau 403 (Forbidden) menandakan folder/file tersebut EKSIS
                    if response.status in (200, 403):
                        exposed_paths.append({
                            "path": path,
                            "http_status": response.status,
                            "severity": "HIGH" if response.status == 200 and (".env" in path or ".git" in path) else "MEDIUM"
                        })
                    conn.close()
                except:
                    continue

            return {
                "module": self.name,
                "target": target,
                "status": "OK",
                "count": len(exposed_paths),
                "exposed_web_files": exposed_paths if exposed_paths else "Secure (No sensitive public files discovered)"
            }

        except Exception as e:
            return {
                "module": self.name,
                "target": target,
                "status": "ERROR",
                "exposed_web_files": [],
                "details": str(e)
            }
