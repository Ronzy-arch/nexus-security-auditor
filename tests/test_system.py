from modules.system_audit import SystemAudit

def test_system_audit_returns_dict():
    result = SystemAudit().run()
    assert isinstance(result, dict)
    assert result["module"] == "Remote OS & Banner Grabber"

def test_system_information_exists():
    result = SystemAudit().run()
    assert "data" in result
    assert "resolved_ip" in result["data"]
