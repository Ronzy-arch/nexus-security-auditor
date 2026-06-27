from modules.patch_audit import PatchAudit

def test_patch_audit_returns_dict():
    result = PatchAudit().run()
    assert isinstance(result, dict)
    assert result["module"] == "Remote Web Patch & Software Audit"

def test_patch_results_structure():
    result = PatchAudit().run()
    assert "results" in result
