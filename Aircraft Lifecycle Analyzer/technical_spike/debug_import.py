import sys
import importlib.util
spec = importlib.util.find_spec('am4')
print("spec:", spec)
if spec:
    print("origin:", spec.origin)
    print("submodule_search_locations:", spec.submodule_search_locations)
