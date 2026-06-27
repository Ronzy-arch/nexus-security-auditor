from modules.file_permission import FilePermissionAudit

def test_permission_audit_returns_dict():
    result = FilePermissionAudit().run()
    assert isinstance(result, dict)
    assert result["module"] == "Remote Security Headers Audit"
