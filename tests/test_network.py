from modules.network_audit import NetworkAudit

def test_network_audit_returns_dict():
    result = NetworkAudit().run()
    assert isinstance(result, dict)
    assert result["module"] == "Remote Connectivity & Origin IP Audit"

def test_network_interfaces_structure():
    result = NetworkAudit().run()
    assert "network_data" in result
