import importlib.util, os
_s = importlib.util.spec_from_file_location("p", os.path.join(os.path.dirname(os.path.abspath(__file__)), "P11_inclass.py"))
_m = importlib.util.module_from_spec(_s); _s.loader.exec_module(_m)
SPEC = _m.spec("furnace", {"domain": ["furnace"], "hot_len": [4, 5, 6], "deliv_period": [2, 3, 4], "draught": [1, 2]})
