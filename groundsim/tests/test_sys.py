from groundsim.tests.test_core import TestBaseClass
from groundsim.mse.sys_payload import calculate_camera_gsd, calculate_camera_fov, calculate_swath, get_imager_frame
from groundsim.mse.sys_obdh import create_vm, init_vm, load_user_task, clear_task_list, run_sheduled_tasks, vm_execute
from math import radians, isclose

def core_dump(vm_memory):
    for item in vm_memory:
        print(["{:x}".format(x) for x in item])

class PayloadTestCases(TestBaseClass):
    def setUp(self):
        self.test_data = {
            "imager": {
                "fov":2.22,
                "d":0.0225,
                "f":0.58,
                "sensor":[4096,4096],
                "pixel":5.5E-6
            },
            "test_alt":500,
            "test_lat":46.1922,
            "test_lon":30.3333,
        }
        self.fp_epsilon = 0.001

    def test_calculate_swath(self):
        result = calculate_swath(self.test_data["imager"]["fov"], self.test_data["test_alt"])
        assert(self.fp_eq(result,19.375)==True)

    def test_calculate_fov(self):
        d = self.test_data["imager"]["d"]
        f = self.test_data["imager"]["f"]
        result = calculate_camera_fov(d,f)
        assert(self.fp_eq(result,2.222)==True)

    def test_calculate_gsd(self):
        p_size = self.test_data["imager"]["pixel"]
        f_len = self.test_data["imager"]["f"]
        p_alt = self.test_data["test_alt"]
        result = calculate_camera_gsd(p_alt, p_size, f_len)
        assert(self.fp_eq(result,4.741)==True)

    def test_get_imager_frame(self):
        result = get_imager_frame(
            self.test_data["imager"]["fov"],
            self.test_data["test_alt"],
            self.test_data["test_lat"],
            self.test_data["test_lon"]
        )
        assert(self.fp_eq(result["top"], 46.279) == True)
        assert(self.fp_eq(result["left"], 30.207) == True)
        assert(self.fp_eq(result["bottom"], 46.105) == True)
        assert(self.fp_eq(result["right"], 30.458) == True)

class OBDHTestCases(TestBaseClass):
    def setUp(self):
        self.test_vm = create_vm()
        self.test_program = [
            "1,1,10,7",
            "OP_LEA, FREG_A, 1, 1",
            "OP_LEA, FREG_B, 1, 2",
            "OP_LEA, FREG_C, 1, 3",
            "OP_FMA, FREG_A, FREG_B, FREG_C",
            "OP_MOV, PRE_MOV_RAM, FREG_C, 3",
            "OP_STR, PRE_STR_FPU, FREG_C",
            "OP_HLT",
            "1.0f",
            "2.0f",
            "1.0f"
        ]
        self.test_snapshot_blank = {
            'VCPU': {
                'ALU_REGISTERS': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'FPU_REGISTERS': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                'FPU_PRCSN': 0.001,
                'VXM_CLOCK': 0,
                'NMF_CLOCK': 0,
                'ADCS_MODE': 0
            },
            'VRAM': {
                'TASK_CONTEXT_STATUS': {},
                'TASK_CONTEXT_WASRUN': {},
                'PROGRAM_CODE_MEMORY': {}
            },
            'VBUS': {
                'CHANNEL_OUT': [],
                'CHANNEL_INP': []
            }
        }

    def test_init_vm(self):
        self.test_vm = init_vm(self.test_vm)
        assert(self.test_vm==self.test_snapshot_blank)
        self.test_vm = {}

    def test_clear_vm(self):
        self.test_vm = init_vm(self.test_vm)
        self.test_vm = load_user_task(self.test_vm, self.test_program)
        self.test_vm = clear_task_list(self.test_vm)
        assert(self.test_vm==self.test_snapshot_blank)
        self.test_vm = {}

    def test_run_vm_task(self):
        self.test_vm = init_vm(self.test_vm)
        print()
        self.test_vm = load_user_task(self.test_vm, self.test_program)
        for item in self.test_vm["VRAM"]["PROGRAM_CODE_MEMORY"].items():
            for i in item[1].items():
                self.test_vm = vm_execute(self.test_vm, i[1])
        self.test_vm = {}

    def test_vm_scheduler(self):
        pass
        #self.test_vm = init_vm(self.test_vm)
        #self.test_vm = load_user_task(self.test_vm, self.test_program)
        #self.test_vm = run_sheduled_tasks(self.test_vm)
        #self.test_vm = {}
