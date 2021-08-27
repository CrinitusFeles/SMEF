__version__ = '0.7.0'

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