import pytest
from src.infrastructure.reports.report_exporter import ReportExporterEngine, ReportFormat


def test_report_exporter_engine():
    analysis = {"document_type": "Legal Contract", "risk_score": 0.65}

    md_report = ReportExporterEngine.generate_report("solution_legal", "contract.pdf", analysis, ReportFormat.MARKDOWN)
    assert "# Executive Intelligence Report: contract.pdf" in md_report
    assert "Risk Score" in md_report
    assert "[1] Section 1" in md_report

    json_report = ReportExporterEngine.generate_report("solution_legal", "contract.pdf", analysis, ReportFormat.JSON)
    assert "contract.pdf" in json_report
