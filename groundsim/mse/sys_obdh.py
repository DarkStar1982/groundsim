from groundsim.mse.lib_splice import process_program_code, unpack32to4x8, unpack_float_from_int

################################################################################
############################ SPLICE VM - DEFINITIONS ###########################
################################################################################
# Opcodes
OP_NOP = 0x00 # No action
OP_MOV = 0x01 # OPCODE|  PREFIX|  REG_A|   DEST|
OP_LEA = 0x02 # OPCODE|  REG_ID|TASK_ID|ADDRESS| (REG_ID can be float or int)
OP_CMP = 0x03 # OPCODE|OPERATOR|  REG_A|  REG_B| (compare register values) OR
              # OPCODE|OPERATOR|TASK_ID| REG_ID| (check task execution status)
OP_SET = 0x04 # OPCODE| INST_ID|  PARAM| REG_ID| (sets instrument parameter to register)
OP_GET = 0x05 # OPCODE| INST_ID|  PARAM| REG_ID| (gets instrument parameter from register)
OP_ACT = 0x06 # OPCODE| INST_ID| ACTION| REG_ID|
OP_HLT = 0x07 # Stop execution
OP_STR = 0x08 # OPCODE|  PREFIX| UNUSED| REG_ID| writes to output
OP_FMA = 0x09 # OPCODE|   REG_A|  REG_B|  REG_C| add and multiply: REG_C = (REG_C*REG_B) - REG_A
OP_FSD = 0x0A # OPCODE|   REG_A|  REG_B|  REG_C| sub and divide: REG_C = (REG_C*REG_B) - REG_A
OP_SIN = 0x0B # OPCODE|  PREFIX|  REG_A|  REG_B| sine:   REG_B = sin(REG_A) ..and arcsin
OP_COS = 0x0C # OPCODE|  PREFIX|  REG_A|  REG_B| cosine: REG_B = cos(REG_A) ...and arccos
OP_TAN = 0x0D # OPCODE|  PREFIX|  REG_A|  REG_B| tan/atan: REG_B = tan(REG_A)
OP_POW = 0x0E # OPCODE|  PREFIX|  REG_A|  REG_B| power: log and roots can be done as well
OP_NOR = 0x0F # OPCODE|   REG_A|  REG_B|  REG_C| REG_C = REG_A NOR NEG_B

# registers
ALU_REG_COUNT = 16
FPU_REG_COUNT = 32

# opcode execution results
EX_OPCODE_FINE = 0x00 #VM opcode executed OK
EX_CHECK_TRUTH = 0x01 #CMP opcode execution result is TRUE
EX_CHECK_FALSE = 0x02 #CMP opcode execution result is FALSE
EX_ACTION_FAIL = 0x03 #Opcode ok, but instrument response is not
EX_BAD_OPERAND = 0x04 #Mismatched opcode and operand
EX_OPC_UNKNOWN = 0x05 #Not able to decode opcode

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
            "PROGRAM_CODE_MEMORY":{}
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

def get_vm_time(p_splice_vm):
    return p_splice_vm

def opcode_mov(p_splice_vm):
    return p_splice_vm

def opcode_lea(p_splice_vm, p_reg_id, p_source_id, p_addr, p_group_id, p_task_id, p_offset):
    # determine global data location
    if p_source_id == p_task_id:
        target_offset = p_offset
    else:
        target_header = unpack32to4x8(p_splice_vm["VRAM"]["PROGRAM_CODE_MEMORY"][p_group_id][p_source_id][0])
        target_offset = target_header[3]
    # load data
    data = p_splice_vm["VRAM"]["PROGRAM_CODE_MEMORY"][p_group_id][p_source_id][p_addr+target_offset];
    if (p_reg_id<0x10):
        p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_id] = data
        return p_splice_vm, EX_OPCODE_FINE
    elif (p_reg_id>0x0F) and (p_reg_id<0x20):
        data_float = unpack_float_from_int(data)
        p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_id] = data_float
        return p_splice_vm, EX_OPCODE_FINE;

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

def opcode_fma(p_splice_vm, p_reg_a, p_reg_b, p_reg_c):
    if  (p_reg_a<0x10) and (p_reg_b<0x10) and (p_reg_c<0x10):
        p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_c] = p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_c] * p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_b]
        p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_c] = p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_c] + p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_a]
        return p_splice_vm, EX_OPCODE_FINE
    elif ((p_reg_a>0x0F) and (p_reg_a<0x20)) and ((p_reg_b>0x0F) and (p_reg_b<0x20)) and ((p_reg_c>0x0F) and (p_reg_c<0x20)):
        p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_c] = p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_c] * p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b]
        p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_c] = p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_c] + p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_a]
        return p_splice_vm, EX_OPCODE_FINE
    else:
        return p_splice_vm, EX_BAD_OPERAND;

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

def get_task_header_ids(p_header):
    header = unpack32to4x8(p_header)
    return header[0], header[1]

def set_vram_content(p_splice_vm, p_dict_name, p_header, p_data):
    group_id, task_id = get_task_header_ids(p_header)
    if group_id not in p_splice_vm["VRAM"][p_dict_name]:
        p_splice_vm["VRAM"][p_dict_name][group_id] = {}
    if task_id not in p_splice_vm["VRAM"][p_dict_name][group_id]:
        p_splice_vm["VRAM"][p_dict_name][group_id][task_id] = {}
    p_splice_vm["VRAM"][p_dict_name][group_id][task_id] = p_data
    return p_splice_vm

def get_vram_content(p_splice_vm, p_dict_name, p_header):
    group_id, task_id = get_task_header_ids(p_header)
    return p_splice_vm["VRAM"][p_dict_name][group_id][task_id]

def check_frequency(p_header):
    return VM_TASK_IS_READY

def vm_execute(p_splice_vm, p_task):
    # print(p_task)
    decoded_header = unpack32to4x8(p_task[0])
    group_id = decoded_header[0]
    task_id = decoded_header[1]
    offset = decoded_header[3]
    ip = 1
    next_opcode = OP_NOP
    task_info = "%s:%s:" % (group_id, task_id)
    while (next_opcode!=OP_HLT) and (ip<len(p_task)):
        word = unpack32to4x8(p_task[ip])
        print ("%s%s" %(task_info, "{:x}".format(p_task[ip])))
        next_opcode = word[0]
        op_a = word[1]
        op_b = word[2]
        op_c = word[3]
        opc_result = EX_OPC_UNKNOWN
        if next_opcode == OP_NOP:
            opc_result = EX_OPCODE_FINE
        if next_opcode == OP_HLT:
            p_splice_vm = set_vram_content(p_splice_vm, "TASK_CONTEXT_STATUS", p_task[0], TASK_COMPLETED)
            return p_splice_vm
        if next_opcode == OP_LEA:
            p_splice_vm, opcode_result = opcode_lea(p_splice_vm, op_a, op_b, op_c, group_id, task_id, offset)
        if next_opcode == OP_FMA:
            p_splice_vm, opcode_result = opcode_fma(p_splice_vm, op_a, op_b, op_c)
        ip = ip + 1
    return p_splice_vm

def load_user_task(p_splice_vm, p_task_code):
    program_bytecode = process_program_code(p_task_code, False)
    p_splice_vm = set_vram_content(p_splice_vm, "TASK_CONTEXT_STATUS", program_bytecode[0], TASK_LOADED_OK)
    p_splice_vm = set_vram_content(p_splice_vm, "TASK_CONTEXT_WASRUN", program_bytecode[0], TASK_TIME_ZERO)
    p_splice_vm = set_vram_content(p_splice_vm, "PROGRAM_CODE_MEMORY", program_bytecode[0], program_bytecode)
    return p_splice_vm

# flush all tasks from memory
def clear_task_list(p_splice_vm):
    p_splice_vm["VRAM"]["PROGRAM_CODE_MEMORY"].clear()
    p_splice_vm["VRAM"]["TASK_CONTEXT_STATUS"].clear()
    p_splice_vm["VRAM"]["TASK_CONTEXT_WASRUN"].clear()
    return p_splice_vm

# add run loop and timing controls?
# REDO!
def run_sheduled_tasks(p_splice_vm):
    # advance VM clocks
    # run loaded tasks
    # for key, item in p_splice_vm["VRAM"]["PROGRAM_CODE_MEMORY"]:
    #    for k, v in item:
    #        if get_vram_content(p_splice_vm, "TASK_CONTEXT_STATUS", v[0]) > TASK_NOTLOADED:
    #            freq = check_frequency(v[0])
    #            if freq == VM_TASK_NOTREADY:
    #                p_splice_vm = set_vram_content(p_splice_vm, "TASK_CONTEXT_STATUS", v[0], TASK_CON_UNMET)
    #            elif freq == VM_TASK_IS_READY:
    #                p_splice_vm = vm_execute(p_splice_vm, item)
    #                p_splice_vm = set_vram_content(p_splice_vm, "TASK_CONTEXT_WASRUN", v[0], get_vm_time(p_splice_vm))
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
