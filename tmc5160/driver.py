from collections import namedtuple
from enum import Enum
import asyncio
import logging
from typing import Literal

import RPi.GPIO as GPIO

from tmc5160 import structs


logger = logging.getLogger(__name__)


class RegisterUnknownException(Exception):
    pass


class RegisterValueError(Exception):
    pass


class RegisterWriteForbidden(Exception):
    pass


class RegisterReadForbidden(Exception):
    pass


Register = namedtuple("Register", ["address", "access_mode", "struct"])
RegisterAccessMode = Enum("RegisterAccessMode", "R W RW RWC")


class RegistersWrapper:
    def __init__(self, tmc5160, registers):
        super().__setattr__("_tmc5160", tmc5160)
        super().__setattr__("_registers", registers)

    def __getattr__(self, name):
        try:
            register = self._registers[name].value
            return self._read(register)
        except KeyError:
            raise RegisterUnknownException()

    def __setattr__(self, name, value):
        try:
            register = self._registers[name].value
            self._write(register, value)
        except KeyError:
            raise RegisterUnknownException()

    def _send_data(self, data_array: list) -> int:
        GPIO.output(self._tmc5160.chip_select_pin, GPIO.LOW)
        response = self._tmc5160.spidev.xfer2(data_array)
        GPIO.output(self._tmc5160.chip_select_pin, GPIO.HIGH)
        return response

    def _read(self, register):
        if register.access_mode not in [
            RegisterAccessMode.R,
            RegisterAccessMode.RW,
            RegisterAccessMode.RWC,
        ]:
            raise RegisterReadForbidden()
        send_buffer = structs.SPIRead.build(dict(address=register.address))
        # Send address so that next message will return the register-data
        self._send_data(send_buffer)
        read_buffer = self._send_data(send_buffer)
        spi_response = structs.SPIResponse.parse(bytes(read_buffer))

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "read - payload_buffer: 0x%s", bytes(spi_response.payload).hex()
            )
            if register.struct:
                logger.debug(
                    "read - payload: %s", register.struct.parse(spi_response.payload)
                )

        if register.struct:
            return register.struct.parse(spi_response.payload)
        else:
            return spi_response.payload

    def _write(self, register, data):
        if register.access_mode not in [RegisterAccessMode.W, RegisterAccessMode.RW]:
            raise RegisterWriteForbidden()
        if register.struct:
            payload_buffer = register.struct.build(data)
        elif isinstance(data, int):
            payload_buffer = data.to_bytes(4, "big")
        else:
            raise RegisterValueError()

        if logger.isEnabledFor(logging.DEBUG):
            # TODO log register-name
            logger.debug("write - payload_buffer: 0x%s", payload_buffer.hex())
            if register.struct:
                logger.debug(
                    "write - payload: %s", register.struct.parse(payload_buffer)
                )

        send_buffer = structs.SPIWrite.build(
            dict(address=register.address, payload=payload_buffer)
        )

        return self._send_data(send_buffer)


class TMC5160:
    class Registers(Enum):
        # General Configuration Registers
        GCONF = Register(0x00, RegisterAccessMode.RW, structs.GCONF)
        #  GSTAT =         Register(0x01, RegisterAccessMode.RWC,  structs.GSTAT)
        #  IFCNT =         Register(0x02, RegisterAccessMode.R,    structs.IFCNT)
        #  SLAVECONF =     Register(0x03, RegisterAccessMode.W,    structs.SLAVECONF)
        #  IOIN =          Register(0x04, RegisterAccessMode.R,    structs.IOIN)
        #  OUTPUT =        Register(0x04, RegisterAccessMode.W,    structs.OUTPUT)
        #  X_COMPARE =     Register(0x05, RegisterAccessMode.W,    structs.X_COMPARE)
        #  OTP_PROG =      Register(0x06, RegisterAccessMode.W,    structs.OTP_PROG)
        #  OTP_READ =      Register(0x07, RegisterAccessMode.R,    struct.OTP_READ)
        #  FACTORY_CONF =  Register(0x08, RegisterAccessMode.RW,   structs.FACTORY_CONF)
        #  SHORT_CONF =    Register(0x09, RegisterAccessMode.W,    structs.SHORT_CONF)
        #  DRV_CONF =      Register(0x0A, RegisterAccessMode.W,    structs.DRV_CONF)
        #  GLOBALSCALER =  Register(0x0B, RegisterAccessMode.W,    structs.GLOBALSCALER)
        #  OFFSET_READ =   Register(0x0C, RegisterAccessMode.R,    structs.OFFSET_READ)

        # Velocity Dependent Driver Feature Control Register Set
        IHOLD_IRUN = Register(0x10, RegisterAccessMode.W, structs.IHOLD_IRUN)
        TPOWERDOWN = Register(0x11, RegisterAccessMode.W, structs.TPOWERDOWN)
        #  TSTEP =        Register(0x12, RegisterAccessMode.R,     structs.TSTEP)
        TPWMTHRS = Register(0x13, RegisterAccessMode.W, structs.TPWMTHRS)
        #  TCOOLTHRS =     Register(0x14, RegisterAccessMode.W,    structs.TCOOLTHRS)
        #  THIGH =         Register(0x15, RegisterAccessMode.W,    structs.THIGH)

        # Ramp Generator Motion Control Register Set
        RAMPMODE = Register(0x20, RegisterAccessMode.RW, structs.RAMPMODE)
        XACTUAL = Register(0x21, RegisterAccessMode.RW, structs.XACTUAL)
        VACTUAL = Register(0x22, RegisterAccessMode.R, structs.VACTUAL)
        VSTART = Register(0x23, RegisterAccessMode.W, structs.VSTART)
        A1 = Register(0x24, RegisterAccessMode.W, structs.A1)
        V1 = Register(0x25, RegisterAccessMode.W, structs.V1)
        AMAX = Register(0x26, RegisterAccessMode.W, structs.AMAX)
        VMAX = Register(0x27, RegisterAccessMode.W, structs.VMAX)
        DMAX = Register(0x28, RegisterAccessMode.W, structs.DMAX)
        D1 = Register(0x2A, RegisterAccessMode.W, structs.D1)
        VSTOP = Register(0x2B, RegisterAccessMode.W, structs.VSTOP)
        #  TZEROWAIT =     Register(0x2C, RegisterAccessMode.W,    structs.TZEROWAIT)
        XTARGET = Register(0x2D, RegisterAccessMode.RW, structs.XTARGET)

        # Ramp Generator Driver Feature Control Register Set
        #  VDCMIN =        Register(0x33, RegisterAccessMode.W,    structs.VDCMIN)
        #  SW_MODE =       Register(0x34, RegisterAccessMode.RW,   structs.SW_MODE)
        RAMP_STAT = Register(0x35, RegisterAccessMode.RWC, structs.RAMP_STAT)
        #  XLATCH =        Register(0x36, RegisterAccessMode.R,    structs.XLATCH)

        # Encoder Registers
        #  ENCMODE =       Register(0x38, RegisterAccessMode.RW,   struct.ENCMODE)
        #  X_ENC =         Register(0x39, RegisterAccessMode.RW,   struct.X_ENC)
        #  ENC_CONST =     Register(0x3A, RegisterAccessMode.W,    struct.ENC_CONST)
        #  ENC_STATUS =    Register(0x3B, RegisterAccessMode.RWC,  struct.ENC_STATUS)
        #  ENC_LATCH =     Register(0x3C, RegisterAccessMode.R,    struct.ENC_LATCH)
        #  ENC_DEVIATION = Register(0x3D, RegisterAccessMode.W,    struct.ENC_DEVIATION)

        # Motor Driver Registers
        #  MSLUT0 =        Register(0x60, RegisterAccessMode.W,    struct.MSLUT0)
        #  MSLUT1 =        Register(0x61, RegisterAccessMode.W,    struct.MSLUT1)
        #  MSLUT2 =        Register(0x62, RegisterAccessMode.W,    struct.MSLUT2)
        #  MSLUT3 =        Register(0x63, RegisterAccessMode.W,    struct.MSLUT3)
        #  MSLUT4 =        Register(0x64, RegisterAccessMode.W,    struct.MSLUT4)
        #  MSLUT5 =        Register(0x65, RegisterAccessMode.W,    struct.MSLUT5)
        #  MSLUT6 =        Register(0x66, RegisterAccessMode.W,    struct.MSLUT6)
        #  MSLUT7 =        Register(0x67, RegisterAccessMode.W,    struct.MSLUT7)
        #  MSLUTSEL =      Register(0x68, RegisterAccessMode.W,    struct.MSLUTSEL)
        #  MSLUTSTART =    Register(0x69, RegisterAccessMode.W,    struct.MSLUTSTART)
        #  MSCNT =         Register(0x6A, RegisterAccessMode.R,    struct.MSCNT)
        #  MSCURACT =      Register(0x6B, RegisterAccessMode.R,    struct.MSCURACT)
        CHOPCONF = Register(0x6C, RegisterAccessMode.RW, structs.CHOPCONF)
        #  COOLCONF =      Register(0x6D, RegisterAccessMode.W,    structs.COOLCONF)
        #  DCCTRL =        Register(0x6E, RegisterAccessMode.W,    structs.DCCTRL)
        #  DRV_STATUS =    Register(0x6F, RegisterAccessMode.R,    structs.DRV_STATUS)
        #  PWMCONF =       Register(0x70, RegisterAccessMode.W,    structs.PWMCONF)
        #  PWM_SCALE =     Register(0x71, RegisterAccessMode.R,    structs.PWM_SCALE)
        #  PWM_AUTO =      Register(0x72, RegisterAccessMode.R,    structs.PWM_AUTO)
        #  LOST_STEPS =    Register(0x73, RegisterAccessMode.R,    structs.LOST_STEPS)

    def __init__(self, spidev, chip_select_pin, enable_pin=None, apply_defaults=True):
        self.spidev = spidev
        self.chip_select_pin = chip_select_pin
        self.enable_pin = enable_pin
        self._init_gpio()
        self._registers = RegistersWrapper(registers=TMC5160.Registers, tmc5160=self)
        self.set_ramp_defaults()
        if apply_defaults:
            self.apply_defaults()

    def _init_gpio(self):
        GPIO.setup(self.chip_select_pin, GPIO.OUT)
        GPIO.output(self.chip_select_pin, GPIO.HIGH)
        if self.enable_pin:
            GPIO.setup(self.enable_pin, GPIO.OUT)

    @property
    def registers(self):
        return self._registers

    def apply_defaults(self):
        self.registers.GCONF = dict(en_pwm_mode=True, multistep_filt=True,)
        self.registers.CHOPCONF = dict(TOFF=3, HSTRT=4, HEND=1, TBL=2, chm=False,)
        self.registers.IHOLD_IRUN = dict(IHOLD=2, IRUN=15, IHOLDDELAY=2,)
        self.registers.TPOWERDOWN = 10
        self.registers.TPWMTHRS = 500
        self.registers.RAMPMODE = "position"
        self.registers.XACTUAL = 0
        self.registers.XTARGET = 0

        self.apply_ramp_defaults()

    def set_ramp_defaults(
        self,
        a1=5000,
        v1=5000,
        d1=5000,
        amax=25000,
        vmax=25000,
        dmax=25000,
        vstart=1,
        vstop=10,
    ):
        self._default_ramp_a1 = a1
        self._default_ramp_v1 = v1
        self._default_ramp_d1 = d1
        self._default_ramp_amax = amax
        self._default_ramp_vmax = vmax
        self._default_ramp_dmax = dmax
        self._default_ramp_vstart = vstart
        self._default_ramp_vstop = vstop

    def apply_ramp_defaults(self):
        self.registers.A1 = self._default_ramp_a1
        self.registers.V1 = self._default_ramp_v1
        self.registers.D1 = self._default_ramp_d1
        self.registers.AMAX = self._default_ramp_amax
        self.registers.VMAX = self._default_ramp_vmax
        self.registers.DMAX = self._default_ramp_dmax
        self.registers.VSTART = self._default_ramp_vstart
        self.registers.VSTOP = self._default_ramp_vstop

    def enable_motor(self):
        if self.enable_pin:
            GPIO.output(self.enable_pin, GPIO.LOW)

    def disable_motor(self):
        if self.enable_pin:
            GPIO.output(self.enable_pin, GPIO.HIGH)

    def get_velocity(self):
        return self.registers.VACTUAL

    async def set_velocity(
        self,
        rampmode: Literal["positive", "negative"],
        vmax=None,
        amax=None,
        wait=False,
    ):
        if rampmode != "positive" and rampmode != "negative":
            raise ValueError("rampmode %s not suported for set_velocity", rampmode)
        self.registers.RAMPMODE = rampmode
        if vmax is not None:
            self.registers.VMAX = vmax
        if amax is not None:
            self.registers.AMAX = amax
        if wait:
            await self.wait_velocity_reached()

    async def wait_velocity_reached(self):
        while not self.registers.RAMP_STAT.velocity_reached:
            await asyncio.sleep(0.1)

    async def stop_motor(self, wait=False):
        self.registers.VMAX = 0
        if wait:
            await self.wait_motor_stopped()

    async def wait_motor_stopped(self):
        while not self.registers.RAMP_STAT.vzero:
            await asyncio.sleep(0.1)

    def get_actual_position(self):
        return self.registers.XACTUAL

    async def set_target_position(self, position, wait=False):
        self.registers.RAMPMODE = "position"
        # Position range is from -2^31 to +(2^31)-1
        maximum_position = (2 ** 31) - 1
        minimum_position = -(2 ** 31)
        # Check if position is within bounds
        if position > maximum_position:
            position = maximum_position
            logger.warning("Maximum position reached! Stopped at max value.")
        elif position < minimum_position:
            position = minimum_position
            logger.warning("Minimum position reached! Stopped at min value.")
        self.registers.XTARGET = position
        if wait:
            await self.wait_target_position_reached()

    async def wait_target_position_reached(self):
        while not self.registers.RAMP_STAT.position_reached:
            await asyncio.sleep(0.1)
