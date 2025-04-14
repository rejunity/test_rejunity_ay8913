'''
Created on Jul 29, 2024

@author: Pat Deegan
@copyright: Copyright (C) 2024 Pat Deegan, https://psychogenic.com
'''

from machine import Pin
import rp2
from rp2 import PIO


from ttboard.demoboard import DemoBoard, Pins

import ttboard.log as logging
log = logging.getLogger(__name__)



#
# Ok the SN76489 register writer
# this thing is a little pio program that does some fancy footwork
# to get around the fact that our chip input pins are split up 
# into 2 blocks
#  CHIPIN_LOW_NIBBLE  CHIPOUT_HIGH_NIBBLE  CHIPIN_HIGHNIBBLE
# so we define the pio output (which talks to the chip input) as a 12 bit thing
# then do some magic Mike dance using the ISR as a swap space, to finally 
# get our outputs right and ready for the chip input pins.
#
# TODO: remove pins set twice
# OLD: This is done twice, so we latch the register, then the value
#      appropriately, by using the side-set stuff (thankfully, those two 
#      bidir pins are sequential).
# TODO: validate state machine can run at 4MHz
@rp2.asm_pio(autopull=True, 
             pull_thresh=16,
             out_shiftdir=PIO.SHIFT_RIGHT, fifo_join=rp2.PIO.JOIN_TX,
             in_shiftdir=PIO.SHIFT_LEFT,
             sideset_init=(PIO.OUT_LOW,)*2, # TODO: should this be only 1 ?
             out_init=(PIO.OUT_LOW,)*4 + (PIO.IN_LOW,)*4 + (PIO.OUT_LOW,)*4)
def sn76489Pwriter():
    # takes about 40 us
    out(isr, 8)         .side(0b1) # /WE=1 flush
    in_(isr, 4)         .side(0b0) # /WE=0 write new data
    mov(pins, isr)      .side(0b0)
    out(isr, 8)         .side(0b0) # TODO: really no need to duplicate this
    in_(isr, 4)         .side(0b0) # but kept it the same way it was done for AY8913
    mov(pins, isr)      .side(0b0).delay(3)

class SN76489PIO:
    '''
        PIO implementation of the SN76489 interface.
        Gives us a good deal more spead (~40us to set a register)
        
        All you need to do to use is:
        
        chip = SN76489PIO(tt)
        
        then call
        
            chip.set_value(value:int)
            
        whenever you like.
    '''
    def __init__(self, tt:DemoBoard, chip_frequency=4000000):
        self.tt = tt 
        
        # make sure /WE is setup and the SEL bits are set to 0
        self.tt.bidir_mode = [Pins.OUT, Pins.OUT, Pins.OUT, Pins.IN, 
                              Pins.IN,  Pins.IN,  Pins.IN,  Pins.IN]
        
        self.tt.bidir_byte = 0
        
        # now hand over control of the tt.pins.in*
        # and the bidirs pins to the PIO state machine
        self.sm = rp2.StateMachine(0, sn76489Pwriter, 
             freq=chip_frequency,
             out_base=tt.pins.ui_in0.raw_pin,
             sideset_base=tt.pins.uio0.raw_pin,
             in_base=tt.pins.uo_out0.raw_pin)
        
        self.runPIO(True)

    def runPIO(self, on:bool=True):
        self.sm.active(on)
        
    def reset(self):
        vol = 0
        for c in range(4): # silence all 4 channels
            self.set_value(0b1001_0000 | (c << 5) | (15-vol))

    def set_value(self, value:int):
        # TODO: remove duplication of value
        self.sm.put((value << 8) | value)
