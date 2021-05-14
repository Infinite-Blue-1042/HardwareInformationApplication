#!/usr/bin/env python
from __future__ import print_function 
import psutil
import os

print(psutil.cpu_percent())
print(psutil.virtual_memory())
print('memory % used:', psutil.virtual_memory()[2])
pid = os.getpid()


py = psutil.Process(pid)
memoryUse = py.memory_info()[0]/2.**30  
print('memory use:', memoryUse)


mem=str(os.popen('free -t -m').readlines())
T_ind=mem.index('T')
mem_G=mem[T_ind+14:-4]
S1_ind=mem_G.index(' ')
mem_T=mem_G[0:S1_ind]


mem_G1=mem_G[S1_ind+8:]
S2_ind=mem_G1.index(' ')
mem_U=mem_G1[0:S2_ind]

mem_F=mem_G1[S2_ind+8:]
print 'Summary = ' + mem_G
print 'Total Memory = ' + mem_T +' MB'
print 'Used Memory = ' + mem_U +' MB'
print 'Free Memory = ' + mem_F +' MB'
