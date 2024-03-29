__version__ = '0.7.5'


# there is problem with version control: qdarkstyle requires python >3.6, but AstraLinux has only 3.5
# UPDATE: have assembled python3.9 for AstraLinux
# import pip
# import importlib.util
#
# def install(package):
#     if hasattr(pip, 'main'):
#         pip.main(['install', package])
#     else:
#         pip._internal.main(['install', package])
#
# def upgrade(package):
#     if hasattr(pip, 'main'):
#         pip.main(['install', package, '--upgrade'])
#     else:
#         pip._internal.main(['install', package, '--upgrade'])
#
# spec = importlib.util.find_spec('qdarkstyle')
# if spec is None:
#     print("qdarkstyle is not installed")
#     install('qdarkstyle')
# upgrade('pyqtgraph')