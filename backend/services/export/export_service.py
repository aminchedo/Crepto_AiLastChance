"""
Export and reporting service for BOLT AI Neural Agent System
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

try:
    import weasyprint  # type: ignore
except Exception:
    weasyprint = None  # Optional in some environments


class ExportService:
    """Data export and report generation."""

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or Path("exports")
        self.base_dir.mkdir(exist_ok=True)

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def export_csv(self, df: pd.DataFrame, name: str) -> Path:
        filename = self.base_dir / f"{name}-{self._timestamp()}.csv"
        df.to_csv(filename, index=False)
        return filename

    def export_excel(self, df: pd.DataFrame, name: str) -> Path:
        try:
            import openpyxl  # noqa: F401
        except Exception as e:  # pragma: no cover - dependency guard
            raise RuntimeError(
                "openpyxl is required for Excel export. Please install openpyxl."
            ) from e
        filename = self.base_dir / f"{name}-{self._timestamp()}.xlsx"
        df.to_excel(filename, index=False)
        return filename

    def export_json(self, data: Any, name: str) -> Path:
        filename = self.base_dir / f"{name}-{self._timestamp()}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        return filename

    def generate_pdf_report(self, html_content: str, name: str) -> Path | None:
        if weasyprint is None:
            return None
        filename = self.base_dir / f"{name}-{self._timestamp()}.pdf"
        weasyprint.HTML(string=html_content).write_pdf(filename)
        return filename


export_service = ExportService()


def get_export_service() -> ExportService:
    return export_service
