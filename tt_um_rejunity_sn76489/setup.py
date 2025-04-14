'''
Created on Jul 30, 2024

@author: Pat Deegan
@copyright: Copyright (C) 2024 Pat Deegan, https://psychogenic.com
'''

from ttboard.demoboard import DemoBoard

import ttboard.log as logging
log = logging.getLogger(__name__)

import ttboard.util.platform as platform

def setup(tt:DemoBoard):
    
    if tt.shuttle.run != 'tt05':
        log.error(f"sn76489 isn't actually on shuttle {tt.shuttle.run}, sorry!")
        return False
    
    log.info("Selecting sn76489 project")
    tt.shuttle.tt_um_rejunity_sn76489.enable()

    
    tt.reset_project(True)
    platform.set_RP_system_clock(126e6)
    tt.clock_project_PWM(4e6)

    tt.reset_project(False)
    
    return True
