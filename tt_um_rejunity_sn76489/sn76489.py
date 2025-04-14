'''
Created on Jul 25, 2024

@author: Pat Deegan
@copyright: Copyright (C) 2024 Pat Deegan, https://psychogenic.com
'''
from ttboard.demoboard import DemoBoard, Pins

import ttboard.util.time as time
import ttboard.log as logging
log = logging.getLogger(__name__)

def wait_clocks(num:int=1):
    for _i in range(num):
        time.sleep_us(1)
        
class SN76489:
    '''
        Pure Python implementation, sans PIO or anything fancy.
        It's clean.  It's slow.  Takes maybe 8ms to set a register
        but it does work and can act as an easy-to-debug reference.
    '''
    def __init__(self, tt:DemoBoard):
        self.tt = tt 
        self._cur_reg = -1
        self._cur_val = -1
        
        self.tt.bidir_mode = [Pins.OUT, Pins.OUT, Pins.OUT, Pins.IN, 
                              Pins.IN,  Pins.IN,  Pins.IN,  Pins.IN]
        
        self.tt.bidir_byte = 0
        
        self.latch_delay_clocks = 0
        
        # need speed
        self._pin_we_bar = self.tt.pins.uio0.raw_pin  #self._pin_bc1 = self.tt.uio0.raw_pin 
        
                
    def reset(self):
        vol = 0
        for c in range(4): # silence all 4 channels
            self.value = 0b1001_0000 | (c << 5) | (15-vol)
    
    @property
    def bus(self):
        return self.tt.input_byte 
    @bus.setter 
    def bus(self, set_to:int):
        self.tt.input_byte = set_to

    @property
    def we(self):
        return ~self.tt.pins.uio0()
    @we.setter 
    def we(self, set_to:int):
        self._pin_we_bar.value(~set_to)
        
        
    @property 
    def sel0(self):
        return self.tt.pins.uio1()
    @sel0.setter 
    def sel0(self, set_to:int):
        self.tt.pins.uio1(set_to)
        
        
    @property 
    def sel1(self):
        return self.tt.pins.uio2()
    @sel1.setter 
    def sel1(self, set_to:int):
        self.tt.pins.uio2(set_to)
        
    
    def clockDivStandard(self):
        self.sel0 = 0
        self.sel1 = 0
        
    def clockDivNone(self):
        self.sel1 = 0 # set 0 first, avoid 11
        self.sel0 = 1
        
    def clockDiv128(self):
        self.sel0 = 0 # set 0 first, avoid 11
        self.sel1 = 1
        
    
    def set_value(self, value):
        self.value = value
    @property 
    def value(self):
        return self._cur_val
    @value.setter
    def value(self, set_to:int):
        self.we = 1
        self.bus = set_to 
        self._cur_val = set_to
        if self.latch_delay_clocks:
            wait_clocks(self.latch_delay_clocks)
        self.we = 0
        
        #log.info(f'Set {self.register} to {set_to}')
        
        
        
        
    
        
