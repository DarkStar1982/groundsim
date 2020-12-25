from groundsim.mse.lib_splice import process_program_code, unpack32to4x8

################################################################################
############################ SPLICE VM - DEFINITIONS ###########################
################################################################################
ALU_REG_COUNT = 16
FPU_REG_COUNT = 32

# Task status definitions
TASK_COMPLETED = 0x000000FF # completed ok
TASK_CON_UNMET = 0x0000007F # task condition not met, either prerequisites or frequency-wise
TASK_ERROR_OPC = 0x0000003F # bad opcode or operand
TASK_LOADED_OK = 0x0000001F # loaded, but not executed yet
TASK_NOTLOADED = 0x00000000 # no task in memory

# Initial timestamp
TASK_TIME_ZERO = 0x00000000 # no task in memory

################################################################################
########################## SPLICE VM - INITIALIZATION ##########################
################################################################################

def create_vm():
    splice_vm = {
        "VCPU": {
            "ALU_REGISTERS":[],
            "FPU_REGISTERS":[],
            "FPU_PRCSN":0.001,
            "VXM_CLOCK":0,
            "NMF_CLOCK":0,
            "ADCS_MODE":0
        },
        "VRAM": {
            "TASK_CONTEXT_STATUS":{},
            "TASK_CONTEXT_WASRUN":{},
            "PROGRAM_CODE_MEMORY":[]
        },
        "VBUS":
        {
            "CHANNEL_OUT":[],
            "CHANNEL_INP":[]
        }

    }
    return splice_vm

def init_vm(p_splice_vm):
    for i in range(0, ALU_REG_COUNT):
        p_splice_vm["VCPU"]["ALU_REGISTERS"].append(0)
    for i in range(0, FPU_REG_COUNT):
        p_splice_vm["VCPU"]["FPU_REGISTERS"].append(0.0)
    return p_splice_vm

def start_vm(p_splice_vm):
    return p_splice_vm

################################################################################
######################## SPLICE VM - EXECUTION CONTROL #########################
################################################################################
def set_task_context_status(p_splice_vm, group_id, task_id, p_task_status):
    if group_id not in p_splice_vm["VRAM"]["TASK_CONTEXT_STATUS"]:
        p_splice_vm["VRAM"]["TASK_CONTEXT_STATUS"][group_id] = {}
    if task_id not in p_splice_vm["VRAM"]["TASK_CONTEXT_STATUS"][group_id]:
        p_splice_vm["VRAM"]["TASK_CONTEXT_STATUS"][group_id][task_id] = {}
    p_splice_vm["VRAM"]["TASK_CONTEXT_STATUS"][group_id][task_id] = p_task_status
    return p_splice_vm

def set_task_context_wasrun(p_splice_vm, group_id, task_id, p_task_wasrun):
    if group_id not in p_splice_vm["VRAM"]["TASK_CONTEXT_WASRUN"]:
        p_splice_vm["VRAM"]["TASK_CONTEXT_WASRUN"][group_id] = {}
    if task_id not in p_splice_vm["VRAM"]["TASK_CONTEXT_WASRUN"][group_id]:
        p_splice_vm["VRAM"]["TASK_CONTEXT_WASRUN"][group_id][task_id] = {}
    p_splice_vm["VRAM"]["TASK_CONTEXT_WASRUN"][group_id][task_id] = p_task_wasrun
    return p_splice_vm

def load_user_task(p_splice_vm, p_task_code):
    program_bytecode = process_program_code(p_task_code, False)
    header = unpack32to4x8(program_bytecode[0])
    group_id = header[0]
    task_id = header[1]
    p_splice_vm = set_task_context_status(p_splice_vm, group_id, task_id, TASK_LOADED_OK)
    p_splice_vm = set_task_context_wasrun(p_splice_vm, group_id, task_id, TASK_TIME_ZERO)
    p_splice_vm["VRAM"]["PROGRAM_CODE_MEMORY"].append(program_bytecode)
    return p_splice_vm

def clear_task_list(p_splice_vm):
    return p_splice_vm

def run_sheduled_tasks(p_splice_vm):
    return p_splice_vm

def reset_vm(p_splice_vm):
    return p_splice_vm

def halt_vm(p_splice_vm):
    return p_splice_vm

################################################################################
#################$####### SPLICE VM - OPCODE EXECUTION #########################
################################################################################

def set_adc_register(p_reg, p_value):
    r_value = 0
    return [p_reg, r_value]

def set_fpu_register(p_reg, p_value):
    r_value = 0
    return [p_reg, r_value]

def set_alu_register(p_reg, p_value):
    r_value = 0
    return [p_reg, r_value]

def opcode_mov(p_splice_vm):
    return p_splice_vm

def opcode_lea(p_splice_vm):
    return p_splice_vm

def opcode_str(p_splice_vm):
    return p_splice_vm

def opcode_cmp(p_splice_vm):
    return p_splice_vm

def opcode_get(p_splice_vm):
    return p_splice_vm

def opcode_set(p_splice_vm):
    return p_splice_vm

def opcode_act(p_splice_vm):
    return p_splice_vm

def opcode_fma(p_splice_vm):
    return p_splice_vm

def opcode_fsd(p_splice_vm):
    return p_splice_vm

def opcode_trg(p_splice_vm):
    return p_splice_vm

def opcode_pow(p_splice_vm):
    return p_splice_vm

def opcode_nor(p_splice_vm):
    return p_splice_vm

def vm_execute(p_splice_vm):
    return p_splice_vm
################################################################################
############################# SATELLITE MESSAGE BUS ############################
################################################################################

def create_bus():
    bus = {
        "adcs":[],
        "comm":[],
        "inst":[],
        "gps":[],
        "log":[]
    }
    return bus

def push_message(p_data_bus, p_channel_id, p_message):
    return p_data_bus

def pull_message(p_data_bus, p_channel_id):
    return p_data_bus

################################################################################
########################### OBDH SIMULATION WRAPPERS ###########################
################################################################################
def initialize_obdh_subsystem(p_obdh_definition):
    p_obdh_subsystem = {
        "splice_vm":create_vm(),
        "data_bus":create_bus()
    }
    p_obdh_subsystem["splice_vm"] = init_vm(p_obdh_subsystem["splice_vm"])
    return p_obdh_subsystem

def load_command_script(p_obdh_subsystem, p_script):
    return p_obdh_subsystem

def obdh_step_forward(p_satellite):
    return p_satellite
