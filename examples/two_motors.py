import time
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


def do_motor_stuff(spi):
    logger.debug("Motor setup")
    m1 = Motor(spidev=spi, chip_select_pin=8)
    m2 = Motor(spidev=spi, chip_select_pin=24)
    m1.set_velocity(direction=Motor.Direction.LEFT, vmax=1000)
    m2.set_velocity(direction=Motor.Direction.LEFT, vmax=1000000)
    time.sleep(5)
    m1.stop_motor()
    time.sleep(1)
    m2.stop_motor()


def main():
    setup_gpio()
    spi = setup_spi()
    do_motor_stuff(spi)
    cleanup_gpio()


if __name__ == "__main__":
    main()
