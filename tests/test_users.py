from modules.user_audit import UserAudit

def test_user_audit_returns_dict():
    result = UserAudit().run()
    assert isinstance(result, dict)
    assert result["module"] == "Remote Identity & SSL Audit"

def test_user_structure():
    result = UserAudit().run()
    assert "identity_data" in result
