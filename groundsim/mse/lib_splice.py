################################################################################
################################# VM DEFINITIONS ###############################
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

# opcode execution results
EX_OPCODE_FINE = 0x00 #VM opcode executed OK
EX_CHECK_TRUTH = 0x01 #CMP opcode execution result is TRUE
EX_CHECK_FALSE = 0x02 #CMP opcode execution result is FALSE
EX_ACTION_FAIL = 0x03 #Opcode ok, but instrument response is not
EX_BAD_OPERAND = 0x04 #Mismatched opcode and operand
EX_OPC_UNKNOWN = 0x05 #Not able to decode opcode
# Instrument Definitions
INST_ADC = 0x01
INST_GPS = 0x02
INST_IMG = 0x03
INST_FPU = 0x04
#public static final byte INST_SDR = 0x05  not supported
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
# VM task frequency constants
FREQ_ONCE = 0x00
FREQ_1MIN = 0x3C #60
FREQ_HOUR = 0x77 #119
FREQ_TMAX = 0x7F #127
VM_TASK_IS_READY = 0x01
VM_TASK_NOTREADY = 0x02
VM_TASK_FINISHED = 0x03
# Task status definitions
TASK_COMPLETED = 0x000000FF # completed ok
TASK_CON_UNMET = 0x0000007F # task condition not met, either prerequisites or frequency-wise
TASK_ERROR_OPC = 0x0000003F # bad opcode or operand
TASK_LOADED_OK = 0x0000001F # loaded, but not executed yet
TASK_NOTLOADED = 0x00000000 # no task in memory
# Initial timestamp
TASK_TIME_ZERO = 0x00000000 # no task in memory
# byte manipulation mask
BYTE_MASK_GET = 0x000000FF

################################################################################
############################## INSTRUCTION DECODER #############################
################################################################################

def pack4x8to32(a, b, c, d):
    result = (a<<24)|(b<<16)|(c<<8)|d;
    return result

def decode_prefix(p_pref):
    return 8

def decode_address(p_addr):
    return 8

def decode_operator(p_oper):
    return 8

def decode_action(p_action):
    return 8

def decode_instrument(p_inst):
    return 8

def decode_parameter(p_param):
    return 8

def decode_register(p_param):
    return 8

def process_code_line(p_str, p_mode):
    return 32

def process_program_code(p_str_list):
    return []
