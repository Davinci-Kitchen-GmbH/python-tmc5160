import asyncio
import logging

from tmc5160 import TMC5160 as Motor
from spidev import SpiDev
import RPi.GPIO as GPIO

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)


def setup_gpio():
    logger.debug("GPIO setup")
    GPIO.setmode(GPIO.BCM)


def cleanup_gpio():
    logger.debug("GPIO cleanup")
    GPIO.cleanup()


def setup_spi():
    logger.debug("SPI setup")
    spi = SpiDev()
    spi.open(bus=0, device=0)
    spi.max_speed_hz = 1000000
    spi.bits_per_word = 8
    spi.loop = False
    spi.mode = 3
    spi.no_cs = True
    return spi


async def do_motor_stuff(spi):
    logger.debug("Motor setup")
    m = Motor(spidev=spi, chip_select_pin=8)

    logger.debug("actual position: %s", m.get_actual_position())
    await m.set_target_position(10000, wait=True)
    logger.debug("actual position: %s", m.get_actual_position())
    await m.set_target_position(0, wait=True)
    logger.debug("actual position: %s", m.get_actual_position())
    await m.set_target_position(10000, wait=True)
    logger.debug("setting velocity with wait")
    await m.set_velocity(direction=Motor.Direction.LEFT, wait=True)
    logger.debug("stopping motor with wait")
    await m.stop_motor(wait=True)


async def main():
    setup_gpio()
    spi = setup_spi()
    await do_motor_stuff(spi)
    cleanup_gpio()


if __name__ == "__main__":
    asyncio.run(main())
