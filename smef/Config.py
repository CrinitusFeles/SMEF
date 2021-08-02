import json
import os


class Config:
    def __init__(self, **kwargs):
        # ===========  New Session window  ================
        self.last_path = kwargs.get('last_path', os.getcwd() + '/output')
        self.last_name = kwargs.get('last_name', '')
        self.connected_sensors = kwargs.get('connected_sensors', [False, False, False, False, False])
        self.comment = ''
        # ====================================================

        # =============== Main Window ===================
        self.graph_title = kwargs.get('graph_title', '')
        self.norma = kwargs.get('norma', False)
        self.norma_val = kwargs.get('norma_val', -146)
        self.units = kwargs.get('units', 'В/м')
        # ===============================================

        # ============== Connection window ===================
        self.terminal_server_ip = kwargs.get('server_ip', '10.6.1.95')
        self.sensor1_port = kwargs.get('sensor1_port', 4001)
        self.sensor2_port = kwargs.get('sensor2_port', 4002)
        self.sensor3_port = kwargs.get('sensor3_port', 4003)
        self.sensor4_port = kwargs.get('sensor4_port', 4004)
        self.sensor5_port = kwargs.get('sensor5_port', 4005)
        self.generator_ip = kwargs.get('generator_ip', '10.6.1.98')
        self.generator_port = kwargs.get('generator_port', 8080)
        # ====================================================

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

