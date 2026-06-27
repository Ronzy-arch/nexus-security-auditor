import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class Reporter:
    def __init__(self, output_dir="reports", template_dir="templates"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def write(self, report):
        json_path = self.output_dir / "report.json"
        html_path = self.output_dir / "report.html"

        with open(json_path, "w", encoding="utf-8") as fp:
            json.dump(report, fp, indent=4)

        try:
            template = self.env.get_template("report.html")

            # Menggunakan target_executed agar visual HTML menampilkan target riil yang ditembak
            rendered = template.render(
                target=report.get("target_executed", "localhost"),
                risk=report.get("risk"),
                results=report.get("results", [])
            )

            with open(html_path, "w", encoding="utf-8") as fp:
                fp.write(rendered)

        except Exception:
            pass

        return {
            "json": str(json_path),
            "html": str(html_path)
        }
