import time
from math import sin, cos, tan, asin, acos, atan, pow, log
from groundsim.mse.lib_splice import process_program_code, unpack32to4x8, unpack_float_from_int, pack_float_to_int

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

# ADCS vectors - stored in read-only FPU registers
ADC_SX = 0x00
ADC_SY = 0x01
ADC_SZ = 0x02
ADC_AX = 0x03
ADC_AY = 0x04
ADC_AZ = 0x05
ADC_QA = 0x06
ADC_QB = 0x07
ADC_QC = 0x08
ADC_QD = 0x09
ADC_MX = 0x0A
ADC_MY = 0x0B
ADC_MZ = 0x0C

# Comparison - integer values
ALU_EQ = 0x01 # equal
ALU_NE = 0x02 # not equal
ALU_GT = 0x03 # greater
ALU_LT = 0x04 # lesser
ALU_GE = 0x05 # greater or equal
ALU_LE = 0x06 # lesser or equal
# Comparison - floating point values
FPU_EQ = 0x07 #same but for FPU
FPU_NE = 0x08
FPU_GT = 0x09
FPU_LT = 0x0A
# Comparison - task execution results
TSX_EQ = 0x0D #task result is equal ...
TSX_NE = 0x0E #task result is not equal to ...

# Instrument Definitions
INST_ADC = 0x01
INST_GPS = 0x02
INST_IMG = 0x03
INST_FPU = 0x04
INST_SDR = 0x05 # not supported!

INST_NMF = 0x06
INST_VXM = 0x07 #set or get internal VM parameter

# ADCS parameter definitions
P_ADC_MODE = 0x01
P_ADC_MAGX = 0x02
P_ADC_MAGY = 0x03
P_ADC_MAGZ = 0x04
P_ADC_SUNX = 0x05
P_ADC_SUNY = 0x06
P_ADC_SUNZ = 0x07
P_ADC_ANGX = 0x08
P_ADC_ANGY = 0x09
P_ADC_ANGZ = 0x0A
P_ADC_QTNA = 0x0B
P_ADC_QTNB = 0x0C
P_ADC_QTNC = 0x0D
P_ADC_QTND = 0x0E
P_ADC_MTQX = 0x0F
P_ADC_MTQY = 0x10
P_ADC_MTQZ = 0x11

# NMF parameters definitions
P_NMF_TIME = 0x01

# VM editable parameters
P_VXM_TIME = 0x01
P_VXM_PRSN = 0x02
P_VXM_TLSC = 0x03
P_VXM_DBUG = 0x04

# FPU constants
P_FPU_NIL = 0x00
P_FPU_ONE = 0x01
P_FPU_EXP = 0x02
P_FPU_PIE = 0x03

# GPS Parameter Definitions
P_GPS_LATT = 0x01
P_GPS_LONG = 0x02
P_GPS_ALTT = 0x03
P_GPS_TIME = 0x04

# Camera Parameters
P_IMG_GAIN_R = 0x01
P_IMG_GAIN_G = 0x02
P_IMG_GAIN_B = 0x03
P_IMG_EXPOSE = 0x04
P_IMG_STATUS = 0x05 #not to be used?
P_IMG_NUMBER = 0x06

# Camera Actions commands
A_IMG_DO_JPG = 0x07
A_IMG_DO_RAW = 0x08
A_IMG_DO_BMP = 0x09
A_IMG_DO_PNG = 0x0A

# ADCS Action definitions
A_ADC_NADIR = 0x05
A_ADC_TOSUN = 0x06
A_ADC_BDOTT = 0x07
A_ADC_TRACK = 0x08
A_ADC_UNSET = 0x09

# Prefixes - MOV instruction addressing modes
PRE_MOV_REG = 0x01
PRE_MOV_RAM = 0x02
PRE_MOV_IND = 0x03

# Prefixes -  STR instruction display modes
PRE_STR_ALU = 0x01
PRE_STR_FPU = 0x02
PRE_STR_BIN = 0x03

# Prefixes -  trigonometry and power functions
PRE_NORMAL = 0x01
PRE_INVERT = 0x02

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

# VM execution task states
VM_TASK_IS_READY = 0x01
VM_TASK_NOTREADY = 0x02
VM_TASK_FINISHED = 0x03

LOG_LEVEL_DEBUG = 0
LOG_LEVEL_INFO = 1
LOG_LEVEL_ERROR = 2

DEFAULT_VM_LOG_LEVEL = 1 # 0, 1 or 2
DEFAULT_VM_TIMESLICE = 1

################################################################################
########################## SPLICE VM - INITIALIZATION ##########################
################################################################################

def create_vm():
    splice_vm = {
        "VCPU": {
            "ALU_REGISTERS":[],
            "FPU_REGISTERS":[],
            "VXM_CLOCK":0, # INTERNAL CLOCK
            "NMF_CLOCK":0, # EXTERNAL CLOCK
        },
        "VRAM": {
            "TASK_CONTEXT_STATUS":{},
            "TASK_CONTEXT_WASRUN":{},
            "PROGRAM_CODE_MEMORY":{}
        },
        "VBUS":
        {
            "INST_LOGS":{
                "OUT":[]
            },
            "INST_ADCS":{
                "ADCS_MODE":0,
                "MAG_VAL_X":0,
                "MAG_VAL_Y":0,
                "MAG_VAL_Z":0,
                "COMMAND_Q":[]
            },
            "INST_GNSS":{
                "LAT":0.0,
                "LON":0.0,
                "ALT":0.0,
                "TME":0
            },
            "INST_IMGR":{
                "GAIN_RED":0.0,
                "GAIN_GRN":0.0,
                "GAIN_BLU":0.0,
                "EXPOSURE":0.0,
                "SNAP_NUM":0,
                "COMMAND_Q":[]
            },
        },
        "VFLAGS": {
            "VM_LOG_LEVEL": DEFAULT_VM_LOG_LEVEL,
            "VM_TIMESLICE": DEFAULT_VM_TIMESLICE,
            "FP_PRECISION": 1.0E-07,
        }

    }
    return splice_vm

def init_vm(p_splice_vm):
    # init external clock?
    for i in range(0, ALU_REG_COUNT):
        p_splice_vm["VCPU"]["ALU_REGISTERS"].append(0)
    for i in range(0, FPU_REG_COUNT):
        p_splice_vm["VCPU"]["FPU_REGISTERS"].append(0.0)
    return p_splice_vm

def start_vm(p_splice_vm):
    millis = int(round(time.time() * 1000))
    p_splice_vm["VCPU"]["NMF_CLOCK"] = millis # EXTERNAL CLOCK
    return p_splice_vm

def reset_vm(p_splice_vm):
    return p_splice_vm

def halt_vm(p_splice_vm):
    return p_splice_vm

################################################################################
############################## SPLICE VM - BUS I/O #############################
################################################################################

def log_message(p_splice_vm, p_str, p_error_level):
    if p_error_level>=p_splice_vm["VFLAGS"]["VM_LOG_LEVEL"]:
        p_splice_vm["VBUS"]["INST_LOGS"]["OUT"].append(p_str)
    return p_splice_vm

################################################################################
########################## SPLICE VM - OPCODE DECODING #########################
################################################################################

def set_adc_register(p_reg, p_value):
    r_value = 0
    return [p_reg, r_value]

def set_fpu_register(p_splice_vm, p_reg_id, p_value):
    if p_reg_id>0x0F and p_reg_id<0x20:
        p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_id] = p_value
        return p_splice_vm, EX_OPCODE_FINE
    else:
        return p_splice_vm, EX_BAD_OPERAND

def set_alu_register(p_splice_vm, p_reg_id, p_value):
    if p_reg_id<0x10:
        p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_id] = p_value
        return p_splice_vm, EX_OPCODE_FINE
    else:
        return p_splice_vm, EX_BAD_OPERAND

def opcode_mov(p_splice_vm, p_prefix, p_reg_id, p_addr, p_group_id, p_task_id, p_offset):
    if p_prefix == PRE_MOV_REG:
        if  (p_reg_id<0x10) and (p_addr<0x10):
            p_splice_vm["VCPU"]["ALU_REGISTERS"][p_addr] = p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_id]
            return p_splice_vm, EX_OPCODE_FINE
        elif (p_reg_id>0x0F) and (p_addr>0x0F):
            p_splice_vm["VCPU"]["FPU_REGISTERS"][p_addr] = p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_id]
            return p_splice_vm, EX_OPCODE_FINE
        else:
            return p_splice_vm, EX_BAD_OPERAND
    if p_prefix == PRE_MOV_RAM:
        if (p_reg_id<0x10):
            data = p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_id]
            p_splice_vm["VRAM"]["PROGRAM_CODE_MEMORY"][p_group_id][p_task_id][p_addr+p_offset] = data
            return p_splice_vm, EX_OPCODE_FINE
        elif (p_reg_id>0x0F):
            data = pack_float_to_int(p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_id])
            p_splice_vm["VRAM"]["PROGRAM_CODE_MEMORY"][p_group_id][p_task_id][p_addr+p_offset] = data
            return p_splice_vm, EX_OPCODE_FINE
        else:
            return p_splice_vm, EX_BAD_OPERAND
    return p_splice_vm, EX_OPC_UNKNOWN

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

def opcode_str(p_splice_vm, p_prefix, p_reg_id, p_task_info):
    if p_prefix == PRE_STR_ALU:
        message_string = "%s%s" % (p_task_info, p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_id])
        p_splice_vm = log_message(p_splice_vm, message_string, LOG_LEVEL_INFO)
        return p_splice_vm, EX_OPCODE_FINE
    if p_prefix == PRE_STR_FPU:
        message_string = "%s%s" % (p_task_info, p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_id])
        p_splice_vm = log_message(p_splice_vm, message_string, LOG_LEVEL_INFO)
        return p_splice_vm, EX_OPCODE_FINE
    if p_prefix == PRE_STR_BIN:
        message_string = "%s%s" % (p_task_info, "{0:b}".format(p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_id]))
        p_splice_vm = log_message(p_splice_vm, message_string, LOG_LEVEL_INFO)
        return p_splice_vm, EX_OPCODE_FINE

    return p_splice_vm, EX_BAD_OPERAND

def opcode_cmp(p_splice_vm, p_oper, p_reg_a, p_reg_b, p_group_id):
    source_id = p_reg_a
    if p_oper == FPU_EQ:
        delta = abs(p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_a]) - abs(p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b])
        if abs(delta) < p_splice_vm["VFLAGS"]["FP_PRECISION"]:
            return EX_CHECK_TRUTH
        else:
            return EX_CHECK_FALSE
    if p_oper == FPU_NE:
        delta = abs(p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_a]) - abs(p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b])
        if abs(delta) > p_splice_vm["VFLAGS"]["FP_PRECISION"]:
            return EX_CHECK_TRUTH
        else:
            return EX_CHECK_FALSE
        pass
    if p_oper == FPU_GT:
        if p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_a] > p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b]:
            return EX_CHECK_TRUTH
        else:
            return EX_CHECK_FALSE
    if p_oper == FPU_LT:
        if p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_a] < p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b]:
            return EX_CHECK_TRUTH
        else:
            return EX_CHECK_FALSE
    if p_oper == ALU_EQ:
        if (p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_a] == p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_b]):
            return EX_CHECK_TRUTH
        else:
            return EX_CHECK_FALSE
    if p_oper == ALU_NE: #<---BUG BELOW, LEFT FOR COMPATIBILITY PURPOSES ONLY!!!
        if (p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_a] == p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_b]):
            return EX_CHECK_TRUTH
        else:
            return EX_CHECK_FALSE
    if p_oper == ALU_GT:
        if (p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_a] > p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_b]):
            return EX_CHECK_TRUTH
        else:
            return EX_CHECK_FALSE
    if p_oper == ALU_LT:
        if (p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_a] < p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_b]):
            return EX_CHECK_TRUTH
        else:
            return EX_CHECK_FALSE
    if p_oper == ALU_GE:
        if (p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_a] >= p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_b]):
            return EX_CHECK_TRUTH
        else:
            return EX_CHECK_FALSE
    if p_oper == ALU_LE:
        if (p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_a] <= p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_b]):
            return EX_CHECK_TRUTH
        else:
            return EX_CHECK_FALSE
    if p_oper == TSX_EQ:
        task_status = p_splice_vm["VRAM"]["TASK_CONTEXT_STATUS"][group_id][source_id]
        if task_status == p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_b]:
            return EX_CHECK_TRUTH
        else:
            return EX_CHECK_FALSE
    if p_oper == TSX_NE:
        task_status = p_splice_vm["VRAM"]["TASK_CONTEXT_STATUS"][group_id][source_id]
        if task_status != p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_b]:
            return EX_CHECK_TRUTH
        else:
            return EX_CHECK_FALSE
    return EX_BAD_OPERAND

def opcode_get(p_splice_vm, p_inst_id, p_param_id, p_reg_id):
    # external system time
    if p_inst_id == INST_NMF:
        if p_param_id == P_NMF_TIME:
            return set_alu_register(p_splice_vm, p_reg_id, get_system_time())
    # Constants
    if p_inst_id == INST_FPU:
        if p_param_id == P_FPU_NIL:
            return set_fpu_register(p_splice_vm, p_reg_id, 0.0)
        if p_param_id == P_FPU_ONE:
            return set_fpu_register(p_splice_vm, p_reg_id, 1.0)
        if p_param_id == P_FPU_EXP:
            return set_fpu_register(p_splice_vm, p_reg_id, 2.71828)
        if p_param_id == P_FPU_PIE:
            return set_fpu_register(p_splice_vm, p_reg_id, 3.14159)
    # internal VM settings
    if p_inst_id == INST_VXM:
        if p_param_id == P_VXM_TIME:
            return set_alu_register(p_splice_vm, p_reg_id, get_vm_time(p_splice_vm))
        if p_param_id == P_VXM_PRSN:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VFLAGS"]["FP_PRECISION"])
        if p_param_id == P_VXM_TLSC:
            return set_alu_register(p_splice_vm, p_reg_id, p_splice_vm["VFLAGS"]["VM_TIMESLICE"])
        if p_param_id == P_VXM_DBUG:
            return set_alu_register(p_splice_vm, p_reg_id, p_splice_vm["VFLAGS"]["VM_LOG_LEVEL"])
    # Imager
    if p_inst_id == INST_IMG:
        if p_param_id == P_IMG_GAIN_R:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VBUS"]["INST_IMGR"]["GAIN_RED"])
        if p_param_id == P_IMG_GAIN_G:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VBUS"]["INST_IMGR"]["GAIN_GRN"])
        if p_param_id == P_IMG_GAIN_B:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VBUS"]["INST_IMGR"]["GAIN_BLU"])
        if p_param_id == P_IMG_EXPOSE:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VBUS"]["INST_IMGR"]["EXPOSURE"])
        if p_param_id == P_IMG_NUMBER:
            return set_alu_register(p_splice_vm, p_reg_id, p_splice_vm["VBUS"]["INST_IMGR"]["SNAP_NUM"])
    # GPS
    if p_inst_id == INST_GPS:
        # call GPS async update reques?
        if p_param_id == P_GPS_LATT:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VBUS"]["INST_GNSS"]["LAT"])
        if p_param_id == P_GPS_LONG:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VBUS"]["INST_GNSS"]["LON"])
        if p_param_id == P_GPS_ALTT:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VBUS"]["INST_GNSS"]["ALT"])
        if p_param_id == P_GPS_TIME:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VBUS"]["INST_GNSS"]["TME"])
    # ADCS
    if p_inst_id == INST_ADC:
        # call ADC async update request?
        if p_param_id == P_ADC_MODE:
            return set_alu_register(p_splice_vm, p_reg_id, p_splice_vm["VBUS"]["INST_ADCS"]["ADCS_MODE"])
        if p_param_id == P_ADC_MAGX:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VBUS"]["INST_ADCS"]["MAG_VAL_X"])
        if p_param_id == P_ADC_MAGY:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VBUS"]["INST_ADCS"]["MAG_VAL_Y"])
        if p_param_id == P_ADC_MAGZ:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VBUS"]["INST_ADCS"]["MAG_VAL_Z"])
        if p_param_id == P_ADC_SUNX:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_SX])
        if p_param_id == P_ADC_SUNY:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_SY])
        if p_param_id == P_ADC_SUNZ:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_SZ])
        if p_param_id == P_ADC_ANGX:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_AX])
        if p_param_id == P_ADC_ANGY:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_AY])
        if p_param_id == P_ADC_ANGZ:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_AZ])
        if p_param_id == P_ADC_QTNA:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_QA])
        if p_param_id == P_ADC_QTNB:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_QB])
        if p_param_id == P_ADC_QTNC:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_QC])
        if p_param_id == P_ADC_QTND:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_QD])
        if p_param_id == P_ADC_MTQX:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_MX])
        if p_param_id == P_ADC_MTQY:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_MY])
        if p_param_id == P_ADC_MTQZ:
            return set_fpu_register(p_splice_vm, p_reg_id, p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_MZ])
    return p_splice_vm, EX_BAD_OPERAND

def opcode_set(p_splice_vm, p_inst_id, p_param_id, p_reg_id):
    # Camera settings
    if p_inst_id == INST_IMG:
        if p_param_id == P_IMG_GAIN_R:
            p_splice_vm["VBUS"]["INST_IMGR"]["GAIN_RED"] = p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_id]
            return p_splice_vm, EX_OPCODE_FINE
        if p_param_id == P_IMG_GAIN_G:
            p_splice_vm["VBUS"]["INST_IMGR"]["GAIN_GRN"] = p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_id]
            return p_splice_vm, EX_OPCODE_FINE
        if p_param_id == P_IMG_GAIN_B:
            p_splice_vm["VBUS"]["INST_IMGR"]["GAIN_BLU"] = p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_id]
            return p_splice_vm, EX_OPCODE_FINE
        if p_param_id == P_IMG_EXPOSE:
            p_splice_vm["VBUS"]["INST_IMGR"]["EXPOSURE"] = p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_id]
            return p_splice_vm, EX_OPCODE_FINE
    # internal VM settings
    if p_inst_id == INST_VXM:
        if p_param_id == P_VXM_PRSN:
            p_splice_vm["VFLAGS"]["FP_PRECISION"] = p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_id]
            return p_splice_vm, EX_OPCODE_FINE
        if p_param_id == P_VXM_TLSC:
            p_splice_vm["VFLAGS"]["VM_TIMESLICE"] = p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_id]
            return p_splice_vm, EX_OPCODE_FINE
        if p_param_id == P_VXM_DBUG:
            return set_alu_register(p_splice_vm, p_reg_id, p_splice_vm["VFLAGS"]["VM_LOG_LEVEL"])
    return p_splice_vm, EX_OPCODE_FINE # Should be EX_BAD_OPERAND, but keeping for compatibility sake

def opcode_act(p_splice_vm, p_inst_id, p_param_id, p_reg_id):
    # Camera operations
    if p_inst_id == INST_IMG:
        if p_param_id == A_IMG_DO_JPG:
            p_splice_vm["VBUS"]["INST_IMGR"]["COMMAND_Q"].append(["TAKE_PHOTO", "JPG"])
            return p_splice_vm, EX_OPCODE_FINE
        if p_param_id == A_IMG_DO_RAW:
            p_splice_vm["VBUS"]["INST_IMGR"]["COMMAND_Q"].append(["TAKE_PHOTO", "RAW"])
            return p_splice_vm, EX_OPCODE_FINE
        if p_param_id == A_IMG_DO_BMP:
            p_splice_vm["VBUS"]["INST_IMGR"]["COMMAND_Q"].append(["TAKE_PHOTO", "BMP"])
            return p_splice_vm, EX_OPCODE_FINE
    # ADCS operations
    if p_inst_id == INST_ADC:
        if p_param_id == A_ADC_NADIR:
            duration = p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_id]
            p_splice_vm["VBUS"]["INST_ADCS"]["COMMAND_Q"].append(["SET_MODE", ["NADIR", duration]])
            return p_splice_vm, EX_OPCODE_FINE
        if p_param_id == A_ADC_TOSUN:
            p_splice_vm["VBUS"]["INST_ADCS"]["COMMAND_Q"].append(["SET_MODE", ["SUN_POINT", duration]])
            return p_splice_vm, EX_OPCODE_FINE
        if p_param_id == A_ADC_UNSET:
            p_splice_vm["VBUS"]["INST_ADCS"]["COMMAND_Q"].append(["SET_MODE", ["NULL", 0]])
            return p_splice_vm, EX_OPCODE_FINE
        if p_param_id == A_ADC_BDOTT:
            return p_splice_vm, EX_OPCODE_FINE # not supported in VM
        if p_param_id == A_ADC_TRACK:
            return p_splice_vm, EX_OPCODE_FINE # not supported in VM
    return p_splice_vm, EX_BAD_OPERAND

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

def opcode_fsd(p_splice_vm, p_reg_a, p_reg_b, p_reg_c):
    if  (p_reg_a<0x10) and (p_reg_b<0x10) and (p_reg_c<0x10):
        if (p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_a] == 0):# <<<ASTRA BUG HERE, LEFT FOR COMPATIBILITY, SHOULD BE "p_reg_b"!
            return EX_BAD_OPERAND
        p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_c] = p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_c] / p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_b]
        p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_c] = p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_c] - p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_a]
        return p_splice_vm, EX_OPCODE_FINE
    elif ((p_reg_a>0x0F) and (p_reg_a<0x20)) and ((p_reg_b>0x0F) and (p_reg_b<0x20)) and ((p_reg_c>0x0F) and (p_reg_c<0x20)):
        if (p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b] <= p_splice_vm["VFLAGS"]["FP_PRECISION"]):
            return EX_BAD_OPERAND
        p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_c] = p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_c] / p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b]
        p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_c] = p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_c] - p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_a]
        return p_splice_vm, EX_OPCODE_FINE
    else:
        return p_splice_vm, EX_BAD_OPERAND;
    return p_splice_vm, EX_BAD_OPERAND

def opcode_trg(p_splice_vm, p_opcode, p_prefix, p_reg_a, p_reg_b):
    if ((p_reg_a>0x0F) and (p_reg_a<0x20)) and ((p_reg_b>0x0F) and (p_reg_b<0x20)):
        if p_prefix == PRE_NORMAL:
            if p_opcode == OP_SIN:
                p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b] = sin(p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_a])
                return p_splice_vm, EX_OPCODE_FINE
            if p_opcode == OP_COS:
                p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b] = cos(p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_a])
                return p_splice_vm, EX_OPCODE_FINE
            if p_opcode == OP_TAN:
                p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b] = tan(p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_a])
                return p_splice_vm, EX_OPCODE_FINE
        elif prefix == PRE_INVERT:
            if p_opcode == OP_SIN:
                p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b] = asin(p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_a])
                return p_splice_vm, EX_OPCODE_FINE
            if p_opcode == OP_COS:
                p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b] = acos(p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_a])
                return p_splice_vm, EX_OPCODE_FINE
            if p_opcode == OP_TAN:
                p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b] = atan(p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_a])
                return p_splice_vm, EX_OPCODE_FINE
        else:
            return p_splice_vm, EX_OPC_UNKNOWN
    else:
        return p_splice_vm, EX_BAD_OPERAND;

def opcode_pow(p_splice_vm, p_prefix, p_reg_a, p_reg_b):
    if ((p_reg_a>0x0F) and (p_reg_a<0x20)) and ((p_reg_b>0x0F) and (p_reg_b<0x20)):
        if p_prefix == PRE_NORMAL:
            result = pow(p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b], p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_a])
            p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b] = result
            return p_splice_vm, EX_OPCODE_FINE
        elif p_prefix == PRE_INVERT:
            p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_b] = log(p_splice_vm["VCPU"]["FPU_REGISTERS"][p_reg_a])
            return p_splice_vm, EX_OPCODE_FINE
        else:
            return p_splice_vm, EX_OPC_UNKNOWN
    else:
          return p_splice_vm, EX_BAD_OPERAND

def opcode_nor(p_splice_vm, p_reg_a, p_reg_b, p_reg_c):
    if (p_reg_a<0x10) and (p_reg_b<0x10) and (p_reg_c<0x10):
        p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_c] = ~(p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_a] | p_splice_vm["VCPU"]["ALU_REGISTERS"][p_reg_b]);
        return p_splice_vm, EX_OPCODE_FINE
    else:
        return p_splice_vm, EX_BAD_OPERAND;

################################################################################
######################### SPLICE VM - MEMORY OPERATIONS ########################
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

################################################################################
########################## SPLICE VM - TIMING CONTROL ##########################
################################################################################

def advance_vm_clocks(p_splice_vm, p_seconds):
    p_splice_vm["VCPU"]["VXM_CLOCK"] = p_splice_vm["VCPU"]["VXM_CLOCK"] + p_seconds*1000
    return p_splice_vm

def check_frequency(p_splice_vm, p_header):
    header = unpack32to4x8(p_header)
    group_id = header[0]
    task_id = header[1]
    interval_code = header[2]
    interval_value = 0
    if interval_code == FREQ_TMAX:
        return VM_TASK_IS_READY
    # check if we have at least attempted to run the task
    if interval_code == FREQ_ONCE:
        task_status = get_vram_content(p_splice_vm, "TASK_CONTEXT_STATUS", p_header)
        if task_status == TASK_COMPLETED:
            return VM_TASK_FINISHED
        else:
            return VM_TASK_IS_READY
    else:
       if interval_code < FREQ_1MIN:
           interval_value = interval_code;
       if (interval_code >=FREQ_1MIN) and (interval_code <FREQ_HOUR):
           interval_value = (interval_code-59)*60
       if (interval_code >=FREQ_HOUR) and (interval_code <FREQ_TMAX):
           interval_value = (interval_code-118)*3600
       last_run_time = get_vram_content(p_splice_vm, "TASK_CONTEXT_WASRUN", p_header)
       time_delta = get_vm_time(p_splice_vm) - last_run_time
       if time_delta>=interval_value:
           return VM_TASK_IS_READY
       else:
           return VM_TASK_NOTREADY

def get_vm_time(p_splice_vm):
    return p_splice_vm["VCPU"]["VXM_CLOCK"]/1000

def get_system_time():
    millis = int(round(time.time() * 1000))
    return millis
################################################################################
######################## SPLICE VM - EXECUTION CONTROL #########################
################################################################################

def vm_execute(p_splice_vm, p_task):
    decoded_header = unpack32to4x8(p_task[0])
    group_id = decoded_header[0]
    task_id = decoded_header[1]
    offset = decoded_header[3]
    ip = 1
    next_opcode = OP_NOP
    task_info = "%s:%s:" % (group_id, task_id)
    while (next_opcode!=OP_HLT) and (ip<len(p_task)):
        word = unpack32to4x8(p_task[ip])
        p_splice_vm = log_message(p_splice_vm, "%s%s" %(task_info, "{:x}".format(p_task[ip])), LOG_LEVEL_DEBUG)
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
        if next_opcode == OP_MOV:
            p_splice_vm, opcode_result = opcode_mov(p_splice_vm, op_a, op_b, op_c, group_id, task_id, offset)
        if next_opcode == OP_LEA:
            p_splice_vm, opcode_result = opcode_lea(p_splice_vm, op_a, op_b, op_c, group_id, task_id, offset)
        if next_opcode == OP_STR:
            p_splice_vm, opcode_result = opcode_str(p_splice_vm, op_a, op_c, task_info)
        if next_opcode == OP_CMP:
            opcode_result = opcode_cmp(p_splice_vm, op_a, op_b, op_c, group_id)
        if next_opcode == OP_GET:
            p_splice_vm, opcode_result = opcode_get(p_splice_vm, op_a, op_b, op_c)
        if next_opcode == OP_SET:
            p_splice_vm, opcode_result = opcode_set(p_splice_vm, op_a, op_b, op_c)
        if next_opcode == OP_ACT:
            p_splice_vm, opcode_result = opcode_act(p_splice_vm, op_a, op_b, op_c)
        if next_opcode == OP_FMA:
            p_splice_vm, opcode_result = opcode_fma(p_splice_vm, op_a, op_b, op_c)
        if next_opcode == OP_FSD:
            p_splice_vm, opcode_result = opcode_fsd(p_splice_vm, op_a, op_b, op_c)
        if next_opcode in [OP_SIN, OP_COS, OP_TAN]:
            p_splice_vm, opcode_result = opcode_trg(p_splice_vm, next_opcode, op_a, op_b, op_c)
        if next_opcode == OP_POW:
            p_splice_vm, opcode_result = opcode_pow(p_splice_vm, op_a, op_b, op_c)
        if next_opcode == OP_NOR:
            p_splice_vm, opcode_result = opcode_nor(p_splice_vm, op_a, op_b, op_c)
        if opcode_result == EX_BAD_OPERAND:
            message_string = "%s%s" % (p_task_info, "ERROR - Bad operand in command word!")
            p_splice_vm = log_message(p_splice_vm, message_string, LOG_LEVEL_ERROR)
            p_splice_vm = set_vram_content(p_splice_vm, "TASK_CONTEXT_STATUS", p_task[0], TASK_ERROR_OPC)
            return p_splice_vm
        if opcode_result == EX_OPC_UNKNOWN:
            message_string = "%s%s" % (p_task_info, "ERROR - Undecodable opcode!")
            p_splice_vm = log_message(p_splice_vm, message_string, LOG_LEVEL_ERROR)
            p_splice_vm = set_vram_content(p_splice_vm, "TASK_CONTEXT_STATUS", p_task[0], TASK_ERROR_OPC)
            return p_splice_vm
        if opcode_result == EX_CHECK_FALSE:
            message_string = "%s%s" % (p_task_info, "Terminating task - execution conditions not met ")
            p_splice_vm = log_message(p_splice_vm, message_string, LOG_LEVEL_INFO)
            p_splice_vm = set_vram_content(p_splice_vm, "TASK_CONTEXT_STATUS", p_task[0], TASK_CON_UNMET)
            return p_splice_vm
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

def run_sheduled_tasks(p_splice_vm):
    # advance vm clocks
    p_splice_vm = advance_vm_clocks(p_splice_vm, p_splice_vm["VFLAGS"]["VM_TIMESLICE"])
    # run loaded tasks
    for item in p_splice_vm["VRAM"]["PROGRAM_CODE_MEMORY"].items():
        for i in item[1].items():
            task_header = i[1][0]
            if get_vram_content(p_splice_vm, "TASK_CONTEXT_STATUS", task_header) > TASK_NOTLOADED:
                freq = check_frequency(p_splice_vm, task_header)
                if freq == VM_TASK_NOTREADY:
                    p_splice_vm = set_vram_content(p_splice_vm, "TASK_CONTEXT_STATUS", task_header, TASK_CON_UNMET)
                elif freq == VM_TASK_IS_READY:
                    p_splice_vm = vm_execute(p_splice_vm, i[1])
                    vm_time = get_vm_time(p_splice_vm)
                    p_splice_vm = set_vram_content(p_splice_vm, "TASK_CONTEXT_WASRUN", task_header, vm_time)
    return p_splice_vm


################################################################################
############################# OBDH SIMULATION CORE #############################
################################################################################
def initialize_obdh_subsystem(p_obdh_definition):
    p_obdh_subsystem = {
        "splice_vm":init_vm(create_vm()),
    }
    return p_obdh_subsystem

def load_command_script(p_obdh_subsystem, p_script):
    p_obdh_subsystem["splice_vm"] = load_user_task(p_obdh_subsystem["splice_vm"], p_script)
    return p_obdh_subsystem

def read_from_data_bus(p_splice_vm, p_satellite_bus):
    # Selected ADCS mode
    p_splice_vm["VBUS"]["INST_ADCS"]["ADCS_MODE"] = p_satellite_bus["adc"]["out"]["mode"]
    # gps vector
    p_splice_vm["VBUS"]["INST_GNSS"]["LAT"] = p_satellite_bus["adc"]["out"]["gps"]["lat"]
    p_splice_vm["VBUS"]["INST_GNSS"]["LON"] = p_satellite_bus["adc"]["out"]["gps"]["lng"]
    p_splice_vm["VBUS"]["INST_GNSS"]["ALT"] = p_satellite_bus["adc"]["out"]["gps"]["alt"]
    p_splice_vm["VBUS"]["INST_GNSS"]["TME"] = p_satellite_bus["adc"]["out"]["gps"]["tme"]
    # mag vector - don't ask why
    p_splice_vm["VBUS"]["INST_ADCS"]["MAG_VAL_X"] = p_satellite_bus["adc"]["out"]["imu"]["mag_x"]
    p_splice_vm["VBUS"]["INST_ADCS"]["MAG_VAL_Y"] = p_satellite_bus["adc"]["out"]["imu"]["mag_y"]
    p_splice_vm["VBUS"]["INST_ADCS"]["MAG_VAL_Z"] = p_satellite_bus["adc"]["out"]["imu"]["mag_z"]
    # sun vector
    p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_SX] = p_satellite_bus["adc"]["out"]["imu"]["sun_x"]
    p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_SY] = p_satellite_bus["adc"]["out"]["imu"]["sun_y"]
    p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_SZ] = p_satellite_bus["adc"]["out"]["imu"]["sun_z"]
    # angular accelerations
    p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_AX] = p_satellite_bus["adc"]["out"]["imu"]["sun_x"]
    p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_AY] = p_satellite_bus["adc"]["out"]["imu"]["sun_y"]
    p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_AZ] = p_satellite_bus["adc"]["out"]["imu"]["sun_z"]
    # quaternions
    p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_QA] = p_satellite_bus["adc"]["out"]["imu"]["qat_a"]
    p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_QB] = p_satellite_bus["adc"]["out"]["imu"]["qat_b"]
    p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_QC] = p_satellite_bus["adc"]["out"]["imu"]["qat_c"]
    p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_QD] = p_satellite_bus["adc"]["out"]["imu"]["qat_d"]
    # magnetorquerer
    p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_MX] = p_satellite_bus["adc"]["out"]["mtq"]["mtq_x"]
    p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_MY] = p_satellite_bus["adc"]["out"]["mtq"]["mtq_y"]
    p_splice_vm["VCPU"]["FPU_REGISTERS"][ADC_MZ] = p_satellite_bus["adc"]["out"]["mtq"]["mtq_z"]

    return p_splice_vm

def write_to_data_bus(p_satellite_bus, p_splice_vm):
    # set parameters, if necessary
    p_satellite_bus["imgr"]["inp"]["gain_r"] = p_splice_vm["VBUS"]["INST_IMGR"]["GAIN_RED"]
    p_satellite_bus["imgr"]["inp"]["gain_g"] = p_splice_vm["VBUS"]["INST_IMGR"]["GAIN_GRN"]
    p_satellite_bus["imgr"]["inp"]["gain_b"] = p_splice_vm["VBUS"]["INST_IMGR"]["GAIN_BLU"]
    p_satellite_bus["imgr"]["inp"]["expose"] = p_splice_vm["VBUS"]["INST_IMGR"]["EXPOSURE"]

    # pop VM command queues, push commands to bus queues
    while len(p_splice_vm["VBUS"]["INST_ADCS"]["COMMAND_Q"])>0:
        top = p_splice_vm["VBUS"]["INST_ADCS"]["COMMAND_Q"].pop()
        p_satellite_bus["adc"]["inq"].append(top)
    while len(p_splice_vm["VBUS"]["INST_IMGR"]["COMMAND_Q"])>0:
        top = p_splice_vm["VBUS"]["INST_IMGR"]["COMMAND_Q"].pop()
        p_satellite_bus["imgr"]["inq"].append(top)

    return p_splice_vm, p_satellite_bus

# run forward for the number of seconds provided
def simulate_obdh_subsystem(p_obdh_subsystem, p_mission, p_seconds):
    data_bus = p_mission["satellite"]["subsystems"]["dbus"]
    for i in range(0, p_seconds):
        p_obdh_subsystem["splice_vm"] = read_from_data_bus(p_obdh_subsystem["splice_vm"], data_bus)
        p_obdh_subsystem["splice_vm"] = run_sheduled_tasks(p_obdh_subsystem["splice_vm"])
        p_obdh_subsystem["splice_vm"], data_bus = write_to_data_bus(data_bus, p_obdh_subsystem["splice_vm"])
    return p_obdh_subsystem, data_bus
