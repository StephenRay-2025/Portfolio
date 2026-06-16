import sys, os
print("__file__:", __file__)
print("cwd:", os.getcwd())
sys_path_add = os.path.join(os.path.dirname(__file__), '..', 'analysis')
print("Adding:", sys_path_add)
sys.path.append(sys_path_add)
print("sys.path:", sys.path)
try:
    import analysis.datasets
    print("Import succeeded")
except Exception as e:
    print("Import failed:", e)
