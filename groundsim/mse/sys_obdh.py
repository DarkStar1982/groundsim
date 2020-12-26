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

# VM task frequency constants
FREQ_ONCE = 0x00
FREQ_1MIN = 0x3C #60
FREQ_HOUR = 0x77 #119
FREQ_TMAX = 0x7F #127
VM_TASK_IS_READY = 0x01
VM_TASK_NOTREADY = 0x02
VM_TASK_FINISHED = 0x03

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
########################## SPLICE VM - OPCODE DECODING #########################
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


################################################################################
######################## SPLICE VM - EXECUTION CONTROL #########################
################################################################################
def check_frequency(p_header):
    return VM_TASK_IS_READY

def get_vm_time(p_splice_vm):
    return 0

def vm_execute(p_splice_vm, p_task):
    # print(p_task)
    return p_splice_vm

def get_task_header_ids(p_header):
    header = unpack32to4x8(p_header)
    return header[0], header[1]

def set_task_context(p_splice_vm, p_dict_name, p_header, p_task_context):
    group_id, task_id = get_task_header_ids(p_header)
    if group_id not in p_splice_vm["VRAM"][p_dict_name]:
        p_splice_vm["VRAM"][p_dict_name][group_id] = {}
    if task_id not in p_splice_vm["VRAM"][p_dict_name][group_id]:
        p_splice_vm["VRAM"][p_dict_name][group_id][task_id] = {}
    p_splice_vm["VRAM"][p_dict_name][group_id][task_id] = p_task_context
    return p_splice_vm

def get_task_context(p_splice_vm, p_dict_name, p_header):
    group_id, task_id = get_task_header_ids(p_header)
    return p_splice_vm["VRAM"][p_dict_name][group_id][task_id]

def load_user_task(p_splice_vm, p_task_code):
    program_bytecode = process_program_code(p_task_code, False)
    p_splice_vm = set_task_context(p_splice_vm, "TASK_CONTEXT_STATUS", program_bytecode[0], TASK_LOADED_OK)
    p_splice_vm = set_task_context(p_splice_vm, "TASK_CONTEXT_WASRUN", program_bytecode[0], TASK_TIME_ZERO)
    p_splice_vm["VRAM"]["PROGRAM_CODE_MEMORY"].append(program_bytecode)
    return p_splice_vm

# flush all tasks from memory
def clear_task_list(p_splice_vm):
    p_splice_vm["VRAM"]["PROGRAM_CODE_MEMORY"].clear()
    p_splice_vm["VRAM"]["TASK_CONTEXT_STATUS"].clear()
    p_splice_vm["VRAM"]["TASK_CONTEXT_WASRUN"].clear()
    return p_splice_vm

# add run loop and timing controls?
def run_sheduled_tasks(p_splice_vm):
    # advance VM clocks
    # run loaded tasks
    for item in p_splice_vm["VRAM"]["PROGRAM_CODE_MEMORY"]:
        if get_task_context(p_splice_vm, "TASK_CONTEXT_STATUS", item[0]) > TASK_NOTLOADED:
            freq = check_frequency(item[0])
            if freq == VM_TASK_NOTREADY:
                p_splice_vm = set_task_context(p_splice_vm, "TASK_CONTEXT_STATUS", item[0], TASK_CON_UNMET)
            elif freq == VM_TASK_IS_READY:
                p_splice_vm = vm_execute(p_splice_vm, item)
                p_splice_vm = set_task_context(p_splice_vm, "TASK_CONTEXT_WASRUN", item[0], get_vm_time(p_splice_vm))
    return p_splice_vm

def reset_vm(p_splice_vm):
    return p_splice_vm

def halt_vm(p_splice_vm):
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

def pull_bus_messages(p_splice_vm, p_data_bus):
    return p_data_bus

def push_bus_messages(p_splice_vm, p_data_bus):
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
    p_obdh_subsystem["splice_vm"] = load_user_task(p_obdh_subsystem["splice_vm"], p_script)
    return p_obdh_subsystem

def obdh_step_forward(p_obdh_subsystem, p_seconds):
    # run for the number of seconds provided
    for i in range(0, p_seconds):
        p_obdh_subsystem["splice_vm"] = run_sheduled_tasks(p_obdh_subsystem["splice_vm"])
        p_obdh_subsystem["splice_vm"] = pull_bus_messages(p_obdh_subsystem["splice_vm"], p_obdh_subsystem["data_bus"])
        p_obdh_subsystem["data_bus"] = push_bus_messages(p_obdh_subsystem["splice_vm"], p_obdh_subsystem["data_bus"])
    return p_obdh_subsystem
