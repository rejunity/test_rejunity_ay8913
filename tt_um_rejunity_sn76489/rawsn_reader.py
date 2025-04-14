'''
Created on Jul 25, 2024

@author: Pat Deegan
@copyright: Copyright (C) 2024 Pat Deegan, https://psychogenic.com
'''
import struct
import ttboard.log as logging
log = logging.getLogger(__name__)

class RawSNReader:
    def __init__(self):
        self._file = None 
        self.systemclock = 0
        self.samplerateHz = 0
        self.numsamps = 0
        self.current_sample_index = 0
        self._cur_sample = None
        self._last_sample = None

    @property 
    def samples_left(self):
        return self.numsamps - self.current_sample_index

    def open(self, fpath:str):
        self.current_sample_index = 0
        f = open(fpath, mode='rb')
        self._file = f

        head_size = self.next_byte()
        head = f.read(head_size)

        self.samplerateHz = head[0]
        self.numsamps = head[1] + 256*head[2]
        log.info(f"Header size: {head_size} sample rate: {self.samplerateHz}Hz packets: {self.numsamps} minutes: {head[3]} seconds: {head[4]}")
                
        self.systemclock = 4_000_000
        log.info(f"System clock frequency should be {self.systemclock}")        
        # log.info(f"Sample rate {self.samplerateHz}Hz")
        # log.info(f"Have {self.numsamps} packets")
        return True    

    def next_byte(self):
        if not self._file:
            return -1
        return int.from_bytes(self._file.read(1), 'big')

    @property 
    def last_sample(self):
        return self._last_sample

    @property
    def next_sample(self):
        if self.current_sample_index >= self.numsamps:
            if self._file is not None:
                self._file.close()
                self._file = None
            return None

        numValues = self.next_byte()
        retList = []
        for _i in range(numValues):
            retList.append(self.next_byte())

        self._last_sample = self._cur_sample
        self._cur_sample = retList

        return retList
