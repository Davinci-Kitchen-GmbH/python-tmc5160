from construct import (
    BitStruct,
    BitsInteger,
    ByteSwapped,
    Bytes,
    Bytewise,
    Const,
    Default,
    Enum,
    Flag,
    Int24sl,
    Int32sb,
    Int32ub,
    Int8ul,
    Padded,
    Padding,
    Struct,
)


EnableFlag = Default(Flag, False)


SPIRead = BitStruct(
    "write" / Const(False, Flag), "address" / BitsInteger(7), Padding(32),
)


SPIWrite = BitStruct(
    "write" / Const(True, Flag),
    "address" / BitsInteger(7),
    "payload" / Bytewise(Bytes(4)),
)


SPIStatus = BitStruct(
    "reset_flag" / Flag,
    "driver_error" / Flag,
    "sg2" / Flag,
    "standstill" / Flag,
    "velocity_reached" / Flag,
    "position_reached" / Flag,
    "status_stop_l" / Flag,
    "status_stop_r" / Flag,
)


SPIResponse = Struct("status" / SPIStatus, "payload" / Bytes(4),)

# Register: 0x00
GCONF = BitStruct(
    Padding(32 - 18),
    "test_mode" / EnableFlag,
    "direct_mode" / EnableFlag,
    "stop_enable" / EnableFlag,
    "small_hysteresis" / EnableFlag,
    "diag1_poscomp_pushpull" / EnableFlag,
    "diag0_int_pushpull" / EnableFlag,
    "diag1_steps_skipped" / EnableFlag,
    "diag1_onstate" / EnableFlag,
    "diag1_index" / EnableFlag,
    "diag1_stall" / EnableFlag,
    "diag0_stall" / EnableFlag,
    "diag0_otpw" / EnableFlag,
    "diag0_error" / EnableFlag,
    "shaft" / EnableFlag,
    "multistep_filt" / EnableFlag,
    "en_pwm_mode" / EnableFlag,
    "faststandstill" / EnableFlag,
    "recalibrate" / EnableFlag,
)

# Register: 0x01
#  GSTAT = BitStruct(
#      Padding(32-3)
#      "uv_cp" / Flag,
#      "drv_err" / Flag,
#      "reset" / Flag,
#  )

# Register: 0x02
#  IFCNT = ByteSwapped(Struct(BytesInteger(2)))

# Register: 0x03
#  SLAVECONF = ByteSwapped(BitsSwapped(BitStruct(
#      "SLAVEADDR" / BitsInteger(8),
#      "SENDDELAY" / BitsInteger(4),
#      Padding(32-12),
#  )))

# Register: 0x04
#  IOIN = ByteSwapped(BitsSwapped(BitStruct(
#      "REFL_STEP" / Flag,
#      "REFR_DIR" / Flag,
#      "ENCB_DCEN_CFG4" / Flag,
#      "ENCA_DCIN_CFG5" / Flag,
#      "DRV_ENN" / Flag,
#      "ENC_N_DCO_CFG6" / Flag,
#      "SD_MODE" / Flag,
#      "SWCOMP_IN" / Flag,
#      Padding(16),
#      "VERSION" / BitsInteger(8, swapped=True),
#  )))

# Register: 0x04
#  OUTPUT = ByteSwapped(BitsSwapped(BitStruct(
#      Flag,
#      Padding(31),
#  )))

# Register: 0x10
IHOLD_IRUN = BitStruct(
    Padding(12),
    "IHOLDDELAY" / BitsInteger(4),
    Padding(3),
    "IRUN" / BitsInteger(5),
    Padding(3),
    "IHOLD" / BitsInteger(5),
)

# Register: 0x11
TPOWERDOWN = ByteSwapped(Padded(4, Int8ul))

# Register: 0x13
# TODO should be 20-bit-integer
TPWMTHRS = Int32ub

# Register: 0x20
# TODO
RAMPMODE = ByteSwapped(
    Padded(4, Enum(Int8ul, position=0, positive=1, negative=2, hold=3))
)

# Register: 0x21
XACTUAL = Int32sb

# Register: 0x22
VACTUAL = ByteSwapped(Padded(4, Int24sl))

# Register 0x23
# TODO
VSTART = None

# Register: 0x24
# TODO
A1 = None

# Register: 0x25
# TODO
V1 = None

# Register: 0x26
# TODO
AMAX = None

# Register: 0x27
# TODO
VMAX = None

# Register: 0x28
# TODO
DMAX = None

# Register: 0x2A
# TODO
D1 = None

# Register: 0x2B
# TODO
VSTOP = None

# Register: 0x2D
XTARGET = Int32sb

# Register: 0x35
RAMP_STAT = BitStruct(
    Padding(32 - 14),
    "status_sg" / Flag,
    "second_move" / Flag,
    "t_zerowait_active" / Flag,
    "vzero" / Flag,
    "position_reached" / Flag,
    "velocity_reached" / Flag,
    "event_pos_reached" / Flag,
    "event_stop_sg" / Flag,
    "event_stop_r" / Flag,
    "event_stop_l" / Flag,
    "status_latch_r" / Flag,
    "status_latch_l" / Flag,
    "status_stop_r" / Flag,
    "status_stop_l" / Flag,
)

# Register: 0x36
#  XLATCH = Int32ub

# Register: 0x6C
CHOPCONF = BitStruct(
    "diss2vs" / EnableFlag,
    "diss2g" / EnableFlag,
    "dedge" / EnableFlag,
    "intpol" / EnableFlag,
    "MRES" / Default(BitsInteger(4), 0),
    "TPFD" / Default(BitsInteger(4), 0),
    "vhighchm" / EnableFlag,
    "vhighfs" / EnableFlag,
    Padding(1),
    "TBL" / Default(BitsInteger(2), 0),
    "chm" / EnableFlag,
    Padding(1),
    "disfdcc" / EnableFlag,
    "fd3" / EnableFlag,
    "HEND" / Default(BitsInteger(4), 0),
    "HSTRT" / Default(BitsInteger(3), 0),
    "TOFF" / Default(BitsInteger(4), 0),
)
