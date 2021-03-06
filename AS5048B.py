# https://github.com/sosandroid/AMS_AS5048B  
# Angular Velocity of Earth 7.2921159 × 10-5  radians per SI second
# 1 grad - 0.01745329 rad
# AS5048B resolution 0.0219°/LSB
# AS5048B Noise 0.06°

import sys
import smbus
import time
import numpy as np
from datetime import datetime

DegreesScale = np.around(360./16383.,5)
RadiansScale = np.around(2*np.pi/16383.,5)

resolution = (0.0219 + 0.06) * 0.01745329
Earth_AV = 7.2921159 * 10**-5
min_loop = resolution/Earth_AV

bus=smbus.SMBus(1)
RE_ADDRESS = 0x40 
RE_ZEROMSB_REG = 0x16 #Zero, most significant byte
RE_ZEROLSB_REG = 0x17 #Zero, least significant byte
RE_ANGLEMSB_REG = 0xFE #Angle, most significant byte
RE_ANGLELSB_REG = 0xFF #Angle, least significant byte

bus.write_byte_data(RE_ADDRESS,RE_ZEROMSB_REG,0x00)
bus.write_byte_data(RE_ADDRESS,RE_ZEROLSB_REG,0x00)
ANG_M = bus.read_byte_data(RE_ADDRESS,RE_ANGLEMSB_REG)
ANG_L = bus.read_byte_data(RE_ADDRESS,RE_ANGLELSB_REG)
bus.write_byte_data(RE_ADDRESS,RE_ZEROMSB_REG,ANG_M)
bus.write_byte_data(RE_ADDRESS,RE_ZEROLSB_REG,ANG_L)

# Start_Time = time.time()
Start_Time = time.monotonic()
loop_Time = 20.
loop_cnt = 0
round_p = 5
ANG_old = 0
Angular = 0
print('Angular Velocity')   
print('{0:<23} {1:<24}'.format('instant','mean') )
#polling
while True:
    try:
        if not (np.around(time.monotonic() - Start_Time,3) >= loop_Time):
            continue 
        loop_cnt += 1
        Start_Time = time.monotonic()
        ANG_M = bus.read_byte_data(RE_ADDRESS,RE_ANGLEMSB_REG)
        ANG_L = bus.read_byte_data(RE_ADDRESS,RE_ANGLELSB_REG)
        ANG = (ANG_M<<6)+(ANG_L & 0x3f)
        # New_Angular = np.around(DegreesScale*ANG,round_p)
        # print(New_Angular)
        Delta_ANG = ANG - ANG_old
        # print('RAW Angular =',ANG,' Delta =',Delta_ANG)
        Delta_Angular = np.around(RadiansScale*Delta_ANG,round_p)
        ANG_old = ANG
        Angular_Velocity_instant = Delta_Angular/loop_Time
        Angular = np.around(RadiansScale*ANG,round_p)
        Angular_Velocity_mean = Angular/(loop_cnt*loop_Time)
        # print('Angular Velocity instant %1.7E'%(Angular_Velocity_instant))
        # print('Angular Velocity mean %1.7E'%(Angular_Velocity_mean))
        print('{0:<23.7E} {1:<24.7E}'.format(Angular_Velocity_instant,Angular_Velocity_mean) )    
    except KeyboardInterrupt:
        sys.exit('\nInterrupted by user')     
