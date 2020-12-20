
def initialize_obdh_subsystem(p_obdh_definition):
    p_obdh_subsystem = {
        "VCPU": {
            "ALU_REGISTERS":[],
            "FPU_REGISTERS":[],
            "FPU_PRECISION":0.0
        },
        "VRAM": {
            "TASK_CONTEXT_STATUS":[],
            "TASK_CONTEXT_WASRUN":[],
            "PROGRAM_CODE_MEMORY":[]
        },
        "ADCS_MODE":0,
        "NMF_CLOCK":0,
        "VXM_CLOCK":0
    }
    return p_obdh_subsystem

def load_command_script(p_obdh_subsystem, p_script):
    return p_obdh_subsystem

def run_obdh(p_satellite):
    return p_satellite
