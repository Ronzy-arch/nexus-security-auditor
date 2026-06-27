from modules.waf_detector import WafDetector

def test_waf_detector_returns_dict():
    result = WafDetector().run()
    assert isinstance(result, dict)
    assert result["module"] == "Advanced WAF & Firewall Detector"

def test_waf_data_structure():
    result = WafDetector().run()
    assert "waf_data" in result
