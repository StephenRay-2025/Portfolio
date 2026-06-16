import sys, os
sys_path_add = os.path.join(os.path.dirname(__file__), '..', 'analysis')
sys.path.append(sys_path_add)
import analysis
print('analysis imported')
print(analysis.__file__)
