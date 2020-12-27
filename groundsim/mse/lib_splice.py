import struct
################################################################################
################################# VM DEFINITIONS ###############################
################################################################################

# Registers - ALU
IREG_A = 0x00
IREG_B = 0x01
IREG_C = 0x02
IREG_D = 0x03
IREG_E = 0x04
IREG_F = 0x05
IREG_G = 0x06
IREG_H = 0x07
IREG_I = 0x08
IREG_J = 0x09
IREG_K = 0x0A
IREG_L = 0x0B
IREG_M = 0x0C
IREG_N = 0x0D
IREG_P = 0x0E
IREG_U = 0x0F

# Registers - FPU
FREG_A = 0x10
FREG_B = 0x11
FREG_C = 0x12
FREG_D = 0x13
FREG_E = 0x14
FREG_F = 0x15
FREG_G = 0x16
FREG_H = 0x17
FREG_I = 0x18
FREG_J = 0x19
FREG_K = 0x1A
FREG_L = 0x1B
FREG_M = 0x1C
FREG_N = 0x1D
FREG_P = 0x1E
FREG_U = 0x1F

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

# ADCS Action definitions
A_ADC_NADIR = 0x05
A_ADC_TOSUN = 0x06
A_ADC_BDOTT = 0x07
A_ADC_TRACK = 0x08
A_ADC_UNSET = 0x09

# Camera Parameter Definitions
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

# GPS Parameter Definitions
P_GPS_LATT = 0x01
P_GPS_LONG = 0x02
P_GPS_ALTT = 0x03
P_GPS_TIME = 0x04

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

# byte manipulation mask
BYTE_MASK_GET = 0x000000FF

################################################################################
############################## DECODE DICTIONARIES #############################
################################################################################
OPCODES = {
    "OP_NOP":OP_NOP,
    "OP_MOV":OP_MOV,
    "OP_LEA":OP_LEA,
    "OP_CMP":OP_CMP,
    "OP_SET":OP_SET,
    "OP_GET":OP_GET,
    "OP_ACT":OP_ACT,
    "OP_HLT":OP_HLT,
    "OP_STR":OP_STR,
    "OP_FMA":OP_FMA,
    "OP_FSD":OP_FSD,
    "OP_SIN":OP_SIN,
    "OP_COS":OP_COS,
    "OP_TAN":OP_TAN,
    "OP_POW":OP_POW,
    "OP_NOR":OP_NOR
}

PREFIXES = {
    "PRE_MOV_REG": PRE_MOV_REG,
    "PRE_MOV_RAM": PRE_MOV_RAM,
    "PRE_MOV_IND": PRE_MOV_IND,
    "PRE_STR_ALU": PRE_STR_ALU,
    "PRE_STR_FPU": PRE_STR_FPU,
    "PRE_STR_BIN": PRE_STR_BIN,
    "PRE_NORMAL" : PRE_NORMAL,
    "PRE_INVERT" : PRE_INVERT,
}

OPERATORS = {
    "ALU_EQ": ALU_EQ,
    "ALU_NE": ALU_NE,
    "ALU_GT": ALU_GT,
    "ALU_LT": ALU_LT,
    "ALU_GE": ALU_GE,
    "ALU_LE": ALU_LE,
    "FPU_EQ": FPU_EQ,
    "FPU_NE": FPU_NE,
    "FPU_GT": FPU_GT,
    "FPU_LT": FPU_LT,
    "TSX_EQ": TSX_EQ,
    "TSX_NE": TSX_NE,
}

ACTIONS = {
    "A_IMG_DO_JPG": A_IMG_DO_JPG,
    "A_IMG_DO_RAW": A_IMG_DO_RAW,
    "A_IMG_DO_BMP": A_IMG_DO_BMP,
    "A_IMG_DO_PNG": A_IMG_DO_PNG,
    "A_ADC_NADIR": A_ADC_NADIR,
    "A_ADC_TOSUN": A_ADC_TOSUN,
    "A_ADC_BDOTT": A_ADC_BDOTT,
    "A_ADC_TRACK": A_ADC_TRACK,
    "A_ADC_UNSET": A_ADC_UNSET,
}

INSTRUMENTS = {
    "INST_ADC": INST_ADC,
    "INST_GPS": INST_GPS,
    "INST_IMG": INST_IMG,
    "INST_FPU": INST_FPU,
    "INST_SDR": INST_SDR,
    "INST_NMF": INST_NMF,
    "INST_VXM": INST_VXM,
}

PARAMETERS = {
    "P_ADC_MODE": P_ADC_MODE,
    "P_ADC_MAGX": P_ADC_MAGX,
    "P_ADC_MAGY": P_ADC_MAGY,
    "P_ADC_MAGZ": P_ADC_MAGZ,
    "P_ADC_SUNX": P_ADC_SUNX,
    "P_ADC_SUNY": P_ADC_SUNY,
    "P_ADC_SUNZ": P_ADC_SUNZ,
    "P_ADC_ANGX": P_ADC_ANGX,
    "P_ADC_ANGY": P_ADC_ANGY,
    "P_ADC_ANGZ": P_ADC_ANGZ,
    "P_ADC_QTNA": P_ADC_QTNA,
    "P_ADC_QTNB": P_ADC_QTNB,
    "P_ADC_QTNC": P_ADC_QTNC,
    "P_ADC_QTND": P_ADC_QTND,
    "P_ADC_MTQX": P_ADC_MTQX,
    "P_ADC_MTQY": P_ADC_MTQY,
    "P_ADC_MTQZ": P_ADC_MTQZ,
    "P_IMG_GAIN_R": P_IMG_GAIN_R,
    "P_IMG_GAIN_G": P_IMG_GAIN_G,
    "P_IMG_GAIN_B": P_IMG_GAIN_B,
    "P_IMG_EXPOSE": P_IMG_EXPOSE,
    "P_IMG_STATUS": P_IMG_STATUS,   # not in use?
    "P_IMG_NUMBER": P_IMG_NUMBER,
    "P_GPS_LATT": P_GPS_LATT,
    "P_GPS_LONG": P_GPS_LONG,
    "P_GPS_ALTT": P_GPS_ALTT,
    "P_GPS_TIME": P_GPS_TIME,
    "P_NMF_TIME": P_NMF_TIME,
    "P_VXM_TIME": P_VXM_TIME,
    "P_VXM_PRSN": P_VXM_PRSN,
    "P_VXM_TLSC": P_VXM_TLSC,
    "P_VXM_DBUG": P_VXM_DBUG,
    "P_FPU_NIL": P_FPU_NIL,
    "P_FPU_ONE": P_FPU_ONE,
    "P_FPU_EXP": P_FPU_EXP,
    "P_FPU_PIE": P_FPU_PIE
}

REGISTERS = {
    "IREG_A": IREG_A,
    "IREG_B": IREG_B,
    "IREG_C": IREG_C,
    "IREG_D": IREG_D,
    "IREG_E": IREG_E,
    "IREG_F": IREG_F,
    "IREG_G": IREG_G,
    "IREG_H": IREG_H,
    "IREG_I": IREG_I,
    "IREG_J": IREG_J,
    "IREG_K": IREG_K,
    "IREG_L": IREG_L,
    "IREG_M": IREG_M,
    "IREG_N": IREG_N,
    "IREG_P": IREG_P,
    "IREG_U": IREG_U,
    "FREG_A": FREG_A,
    "FREG_B": FREG_B,
    "FREG_C": FREG_C,
    "FREG_D": FREG_D,
    "FREG_E": FREG_E,
    "FREG_F": FREG_F,
    "FREG_G": FREG_G,
    "FREG_H": FREG_H,
    "FREG_I": FREG_I,
    "FREG_J": FREG_J,
    "FREG_K": FREG_K,
    "FREG_L": FREG_L,
    "FREG_M": FREG_M,
    "FREG_N": FREG_N,
    "FREG_P": FREG_P,
    "FREG_U": FREG_U
}

################################################################################
############################### HELPER FUNCTIONS ###############################
################################################################################

def pack4x8to32(a, b, c, d):
    result = (a<<24)|(b<<16)|(c<<8)|d
    return result

def unpack32to4x8(p_input):
    a = (p_input>>24) & BYTE_MASK_GET
    b = (p_input>>16) & BYTE_MASK_GET
    c = (p_input>>8) & BYTE_MASK_GET
    d = p_input & BYTE_MASK_GET
    return [a, b, c, d]

def unpack_float_from_int(p_i):
    packed_v = struct.pack('>l', p_i)
    f = struct.unpack('>f', packed_v)[0]
    return f

def pack_float_to_int(p_f):
    packed_v = struct.pack('<f', p_f)
    i = struct.unpack('<I', packed_v)[0]
    return i
################################################################################
############################# INSTRUCTION DECODERS #############################
################################################################################
def decode_symbol(p_dict, p_data):
    try:
        p_data = p_data.strip()
        return p_dict[p_data]
    except KeyError:
        return -1

def decode_address(p_addr):
    return int(p_addr)

def decode_prefix(p_pref):
    return decode_symbol(PREFIXES, p_pref)

def decode_operator(p_oper):
    return decode_symbol(OPERATORS, p_oper)

def decode_action(p_action):
    return decode_symbol(ACTIONS, p_action)

def decode_instrument(p_inst):
    return decode_symbol(INSTRUMENTS, p_inst)

def decode_parameter(p_param):
    return decode_symbol(PARAMETERS, p_param)

def decode_register(p_rreg):
    return decode_symbol(REGISTERS, p_rreg)

################################################################################
############################## SOURCE LINE DECODER #############################
################################################################################
def process_code_line(p_str, p_mode):
    line_values = p_str.split(",")
    if p_mode == 0:
        group_id = int(line_values[0])
        task_id = int(line_values[1])
        freq = int(line_values[2])
        length = int(line_values[3])
        bytecode = pack4x8to32(group_id, task_id, freq, length)
        p_mode = p_mode + 1
        return [p_mode, bytecode]
    if p_mode == 1:
        opcode = line_values[0]
        if opcode == "OP_NOP":
            bytecode = pack4x8to32(OP_NOP, OP_NOP, OP_NOP, OP_NOP)
            return [p_mode, bytecode]
        if opcode == "OP_HLT":
            bytecode = pack4x8to32(OP_HLT, OP_NOP, OP_NOP, OP_NOP)
            p_mode = p_mode + 1
            return [p_mode, bytecode]
        if opcode == "OP_LEA":
            op_a = decode_register(line_values[1])
            op_b = decode_address(line_values[2])
            op_c = decode_address(line_values[3])
            bytecode = pack4x8to32(OP_LEA, op_a, op_b, op_c)
            return [p_mode, bytecode]
        if opcode == "OP_MOV":
            op_a = decode_prefix(line_values[1])
            op_b = decode_register(line_values[2])
            op_c =0
            if op_a == PRE_MOV_REG:
                op_c = decode_register(line_values[3])
            elif op_a == PRE_MOV_RAM:
                op_c= decode_address(line_values[3])
            bytecode = pack4x8to32(OP_MOV, op_a, op_b, op_c)
            return [p_mode, bytecode]
        if opcode == "OP_CMP":
            op_a = decode_operator(line_values[1])
            op_c = decode_register(line_values[3])
            if (op_a == TSX_EQ) | (op_a == TSX_NE):
                op_b = decode_address(line_values[2])
            else:
                op_b = decode_register(line_values[2])
            bytecode = pack4x8to32(OP_CMP, op_a, op_b, op_c);
            return [p_mode, bytecode]
        if opcode == "OP_GET":
            op_a = decode_instrument(line_values[1])
            op_b = decode_parameter(line_values[2])
            op_c = decode_register(line_values[3])
            bytecode = pack4x8to32(OP_GET, op_a, op_b, op_c)
            return [p_mode, bytecode]
        if opcode == "OP_SET":
            op_a = decode_instrument(line_values[1])
            op_b = decode_parameter(line_values[2])
            op_c = decode_register(line_values[3])
            bytecode = pack4x8to32(OP_SET, op_a, op_b, op_c);
            return [p_mode, bytecode]
        if opcode == "OP_ACT":
            op_a = decode_instrument(line_values[1])
            op_b = decode_action(line_values[2])
            op_c = decode_register(line_values[3])
            bytecode = pack4x8to32(OP_ACT, op_a, op_b, op_c);
            return [p_mode, bytecode]
        if opcode == "OP_STR":
            op_a = decode_prefix(line_values[1])
            op_c = decode_register(line_values[2])
            bytecode = pack4x8to32(OP_STR, op_a, OP_NOP, op_c)
            return [p_mode, bytecode]
        if opcode == "OP_FMA":
            op_a = decode_register(line_values[1])
            op_b = decode_register(line_values[2])
            op_c = decode_register(line_values[3])
            bytecode = pack4x8to32(OP_FMA, op_a, op_b, op_c)
            return [p_mode, bytecode]
        if opcode == "OP_FSD":
            op_a = decode_register(line_values[1])
            op_b = decode_register(line_values[2])
            op_c = decode_register(line_values[3])
            bytecode = pack4x8to32(OP_FSD, op_a, op_b, op_c)
            return [p_mode, bytecode]
        if opcode == "OP_SIN":
            op_a = decode_prefix(line_values[1])
            op_b = decode_register(line_values[2])
            op_c = decode_register(line_values[3])
            bytecode = pack4x8to32(OP_SIN, op_a, op_b, op_c)
            return [p_mode, bytecode]
        if opcode == "OP_COS":
            op_a = decode_prefix(line_values[1])
            op_b = decode_register(line_values[2])
            op_c = decode_register(line_values[3])
            bytecode = pack4x8to32(OP_COS, op_a, op_b, op_c)
            return [p_mode, bytecode]
        if opcode == "OP_TAN":
            op_a = decode_prefix(line_values[1])
            op_b = decode_register(line_values[2])
            op_c = decode_register(line_values[3])
            bytecode = pack4x8to32(OP_TAN, op_a, op_b, op_c)
            return [p_mode, bytecode]
        if opcode == "OP_POW":
            op_a = decode_prefix(line_values[1])
            op_b = decode_register(line_values[2])
            op_c = decode_register(line_values[3])
            bytecode = pack4x8to32(OP_POW, op_a, op_b, op_c)
            return [p_mode, bytecode]
        if opcode == "OP_NOR":
            op_a = decode_register(line_values[1])
            op_b = decode_register(line_values[2])
            op_c = decode_register(line_values[3])
            bytecode = pack4x8to32(OP_NOR, op_a, op_b, op_c)
            return [p_mode, bytecode]
        # if unable to decode
        raise Exception("Unrecognized instruction")
    if p_mode == 2:
        tail = p_str[-1]
        head = p_str[:-1]
        if tail == 'f':
            head = float(head)
            str_bytes = hex(struct.unpack('<I', struct.pack('<f', head))[0])
            bytecode = int(str_bytes[2:], 16)
        if tail == 'i':
            bytecode = int(head)
        return [p_mode, bytecode]

################################################################################
############################## SOURCE FILE DECODER #############################
################################################################################
def process_program_code(p_str_list, to_hex_str=True):
    output = []
    mode = 0
    for item in p_str_list:
        line_output = process_code_line(item, mode)
        mode = line_output[0]
        bytecode_str = line_output[1]
        if to_hex_str:
            output.append("{:x}".format(bytecode_str))
        else:
            output.append(bytecode_str)
    return output
