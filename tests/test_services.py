from modules.service_audit import ServiceAudit

def test_service_audit_returns_dict():
    result = ServiceAudit().run()
    assert isinstance(result, dict)
    assert result["module"] == "Remote Port Scanner"
