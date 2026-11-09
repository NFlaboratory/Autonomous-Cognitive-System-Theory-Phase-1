import importlib.util, os
_s = importlib.util.spec_from_file_location("p", os.path.join(os.path.dirname(os.path.abspath(__file__)), "P11_inclass.py"))
_m = importlib.util.module_from_spec(_s); _s.loader.exec_module(_m)
SPEC = _m.spec("minacs", {"domain": ["minacs"], "cold_len": [2, 3, 4], "regrow_period": [2, 3, 5], "gift_events": [0, 3]})
