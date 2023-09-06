# import argparse
# from main_window.main_window import main
# from smef.demo_server import DemoServer
#
#
# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='SMEF client')
#     parser.add_argument('-d', '--demo', help='start program with demo server', action='store_true')
#     # parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
#     args = parser.parse_args()
#     if args.demo:
#         print('Starting demo server')
#         server = DemoServer(debug_print=False)
#         server.start_server()
#         main()
#     else:
#         print('Starting without demo server')
#         main()
from smef.fi7000_interface.backend import main

if __name__ == '__main__':
    main()
