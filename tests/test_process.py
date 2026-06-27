from modules.process_audit import ProcessAudit

def test_process_audit_returns_dict():
    result = ProcessAudit().run()
    assert isinstance(result, dict)
    assert result["module"] == "Remote Vulnerability Analyzer"

def test_process_structure():
    result = ProcessAudit().run()
    assert "vulnerabilities_found" in result
