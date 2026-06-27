from modules.vulnerability_scanner import VulnerabilityScanner

def test_vulnerability_scanner_returns_dict():
    result = VulnerabilityScanner().run()
    assert isinstance(result, dict)
    assert result["module"] == "Remote Web App Vulnerability Scanner"

def test_vulnerability_structure():
    result = VulnerabilityScanner().run()
    assert "vulnerabilities_found" in result
