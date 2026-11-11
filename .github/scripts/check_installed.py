"""CI: installed wheel, all native tests and independently specified references."""
from pathlib import Path
import json, math, os, subprocess, sys, tempfile, unittest
root=Path(__file__).resolve().parents[2]
wheel=next((root/"dist").glob("*.whl"))
subprocess.run([sys.executable,"-m","pip","install","--no-deps","--force-reinstall",str(wheel)],check=True)
# Avoid package imports from the repository; all resources come from the wheel.
import pfandbriefcalc as p
assert not Path(p.__file__).resolve().is_relative_to(root/"src")
with tempfile.TemporaryDirectory() as temp:
    previous_cwd = Path.cwd()
    try:
        os.chdir(temp)
        suite=unittest.defaultTestLoader.discover(str(root/"tests"))
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful(): raise SystemExit(1)
        references=json.loads((Path(p.__file__).parent/"resources/shared_oracles.json").read_text())["cases"]
        def equal(a,b):
            if isinstance(a,list): return isinstance(b,(list,tuple)) and len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
            if isinstance(a,(int,float)) and not isinstance(a,bool): return isinstance(b,(int,float)) and not isinstance(b,bool) and math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-8)
            return a==b
        for case in references:
            try: output=getattr(p,case["function"])(**case["arguments"]).as_dict()
            except p.PfandbriefError as e:
                assert e.code==case["error"],case["id"]
                continue
            assert case["error"] is None,case["id"]
            for path,expected in case["expected"].items():
                value=output
                for part in path.strip("/").split("/"): value=value[int(part)] if isinstance(value,(list,tuple)) else value[part]
                assert equal(expected,value),(case["id"],path,expected,value)
        print("Independent references passed:",len(references))
    finally:
        # Windows cannot delete a directory while it is the process working directory.
        os.chdir(previous_cwd)
