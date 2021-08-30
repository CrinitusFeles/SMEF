__version__ = '0.7.2'

try:
    from .mainwindow import Ui_MainWindow
    # from .SessionViewer import *
    from .app_logger import *
    from .CustomPlot import *
    from .double_range_slider import *
    from .utils import *
    from .ConnectionsSettings import *
    from .GeneratorSettings import *
    from .NewSession import *
    from .Config import *
    from .sensor_commands import *
    from .app_logger import *
except Exception as ex:
    from mainwindow import Ui_MainWindow
    # from SessionViewer import *
    from app_logger import *
    from CustomPlot import *
    from double_range_slider import *
    from utils import *
    from ConnectionsSettings import *
    from GeneratorSettings import *
    from NewSession import *
    from Config import *
    from sensor_commands import *
    from app_logger import *

# there is problem with version control: qdarkstyle requires python >3.6, but AstraLinux has only 3.5
import pip
import importlib.util

def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])

spec = importlib.util.find_spec('qdarkstyle')
if spec is None:
    print("qdarkstyle is not installed")
    install('qdarkstyle')