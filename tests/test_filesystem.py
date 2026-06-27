from modules.filesystem_audit import FilesystemAudit

def test_filesystem_audit_returns_dict():
    result = FilesystemAudit().run()
    assert isinstance(result, dict)
    assert result["module"] == "Remote Web Filesystem & Path Audit"

def test_filesystem_structure():
    result = FilesystemAudit().run()
    assert "exposed_web_files" in result
