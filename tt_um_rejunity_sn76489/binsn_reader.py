'''
Created on Jul 25, 2024

@author: Pat Deegan
@copyright: Copyright (C) 2024 Pat Deegan, https://psychogenic.com
'''
import struct
import ttboard.log as logging
log = logging.getLogger(__name__)

# def load_sn76489_bin(filename, verbose=False):
#     f = open(filename, mode="rb")
#     data = f.read()
#     f.close()
#     print(filename, len(data))
#     print("header size: ", data[0], "playback rate: ", data[1], "packets: ", data[2] + 256*data[3], "minutes: ", data[4], "seconds: ", data[5]);
#     playback_rate = data[1]
#     packets = data[2] + 256*data[3]
#     offset = data[0] + 1
#     print("titles size:", data[offset], "title: ", data[offset + 1: offset + 1 + data[offset]])
#     offset += data[offset] + 1
#     print("author size:", data[offset], "author: ", data[offset + 1: offset + 1 + data[offset]])
#     offset += data[offset] + 1

#     # cut the header
#     data = data[offset:len(data)]
#     offset = 0

#     jagged = []
#     for i in range(packets):
#         jagged.append(data[offset+1:offset+1+data[offset]])
#         if verbose: print("packet", i, "size:", data[offset], "data: ", jagged[-1])
#         offset += data[offset] + 1
#     if verbose: print(packets, offset, len(data), int(data[offset]), int(data[-1]))
#     assert data[offset    ] == 0x00
#     assert data[offset + 1] == 0xff

#     assert packets == len(jagged)
#     return jagged, playback_rate

class BinSNReader:
    def __init__(self, skip_duplicate_reg_settings:bool=True):
        self._file = None 
        self.systemclock = 0
        self.samplerateHz = 0
        self.numsamps = 0
        self.current_sample_index = 0
        self._cur_sample = None
        self._last_sample = None
        self.skip_duplicate_reg_settings = skip_duplicate_reg_settings

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

    # def next_registers_list(self):
    #     if self.current_sample_index >= self.numsamps:
    #         if self._file is not None:
    #             self._file.close()
    #             self._file = None
    #         return None
        
    #     numSamps = self.next_byte()
    #     retList = []
    #     for _i in range(numSamps):
    #         retList.append([self.next_byte(), self.next_byte()])
            
    #     return retList
    
    # def next_sample(self):
    #     registerslist = self.next_registers_list()
    #     numSamps = len(registerslist)
    #     if registerslist is None or not numSamps:
    #         return None
    #     samp = Sample(self.current_sample_index, numSamps)
    #     for rs in registerslist:
    #         samp.add_register(RegisterValue(rs[0], rs[1]))
            
    #     self._last_sample = self._cur_sample
    #     self._cur_sample = samp
    #     return samp 
    
    # def next_registers_to_set(self):
    #     samp = self.next_sample()
    #     if samp is None:
    #         return None
        
    #     allRegs = samp.registers
    #     if not self.skip_duplicate_reg_settings:
    #         return allRegs 
        
    #     last_samp = self.last_sample
    #     if last_samp is None:
    #         return allRegs
        
    #     retList = []
    #     for reg in allRegs:
    #         if (not last_samp.has_register(reg.id)) or last_samp.get_register(reg.id).value != reg.value:
    #             retList.append(reg) 
        
    #     return retList
            
        
        
        
        
        
