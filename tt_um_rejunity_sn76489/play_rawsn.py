'''
Created on Jul 25, 2024

@author: Pat Deegan
@copyright: Copyright (C) 2024 Pat Deegan, https://psychogenic.com
'''

from ttboard.demoboard import DemoBoard

import ttboard.log as logging
log = logging.getLogger(__name__)

from examples.tt_um_rejunity_sn76489.binsn_reader import RawSNReader
from examples.tt_um_rejunity_sn76489.sn76489 import SN76489
from examples.tt_um_rejunity_sn76489.sn76489PIO import SN76489PIO
from examples.tt_um_rejunity_sn76489.setup import setup
import ttboard.util.time as time 

DefaultFile = '/mission76496.rawsn'
def runPurePython(file_to_play:str=DefaultFile):
    tt = DemoBoard.get()
    if not setup(tt):
        return False 
    reader = RawSNReader()
    if not reader.open(file_to_play):
        print(f"Could not open {file_to_play}!")
        return False 
    
    chip = SN76489(tt)
    return playLoop(reader, chip)
    

def run(file_to_play:str=DefaultFile):
    tt = DemoBoard.get()
    if not setup(tt):
        return False 
    
    return play(file_to_play)
    
    
def play(file_to_play:str=DefaultFile):
    
    reader = RawSNReader()
    if not reader.open(file_to_play):
        print(f"Could not open {file_to_play}!")
        return False 
    
    chip = SN76489PIO(DemoBoard.get(), reader.systemclock)
    return playLoop(reader, chip)


def playLoopOO(reader:RawSNReader, chip):
    return playLoop(reader, chip)

def playLoop(reader:RawSNReader, chip):
    delayMs = int(1000/reader.samplerateHz)
    while reader.samples_left:
        tnow = time.ticks_us()
        packet = reader.next_sample
        if packet is None:
            return True
        for val in packet:
            chip.set_value(val)
        #log.info('-')
        msToWait = int(delayMs - ((time.ticks_us() - tnow)/1000))
        #print(msToWait)
        if msToWait > 0:
            time.sleep_ms(msToWait)

    stop()
    return True

def stop():
    chip = SN76489PIO(DemoBoard.get())
    chip.reset() # sets the volume down on all channels
