from pprint import pprint
import sys
from math import cos, sin, sqrt, acos, asin, atan2, pow as pow_f
import os
from rotation_math import tsp_to_r



def _generate_ow_code(trigger, t1, t2, variable, stuck_value):
    """ Example 
        trigger = 'u.sequence'
        t1 = '1000'
        t2 = '1100'
        variable = ['u.delay[0]', 'u.delay[1]']
        stuck_value = ['100','110']

        if(u.sequence > 1000 && u.sequqnce < 1100) {
            u.delay[0] = 100;
            u.delay[1] = 110;
        }
    """
    assert(len(variable) == len(stuck_value))
    code = 'if(%s>%s && %s<%s) {' % \
            (trigger, t1, trigger, t2)
    for v, s in zip(variable, stuck_value):
        l = '%s=%s;' % (v,s)
        code = code + l
    code = code + '}'
    return code

def generate_add_code(trigger, t1, t2, variable, stuck_value):
    """ Example 
        trigger = 'u.sequence'
        t1 = '1000'
        t2 = '1100'
        variable = ['u.delay[0]', 'u.delay[1]']
        stuck_value = ['100','110']

        if(u.sequence > 1000 && u.sequqnce < 1100) {
            u.delay[0] += 100;
            u.delay[1] += 110;
        }
    """
    assert(len(variable) == len(stuck_value))
    code = 'if(%s>%s && %s<%s) {' % \
            (trigger, t1, trigger, t2)
    for v, s in zip(variable, stuck_value):
        l = '%s+=%s;' % (v,s)
        code = code + l
    code = code + '}'
    return code

def _generate_delay_code(trigger, t1, t2, usec):
    """ Example: assumes the source code includes unistd.h
        trigger = 'u.sequence'
        t1 = '1000'
        t2 = '1100'
        length = '100' in usec

        if(u.sequence > 1000 && u.sequqnce < 1100) {
            usleep(100)
        }
    """
    code = 'if(%s>%s && %s<%s) {usleep(%s);}' % \
            (trigger, t1, trigger, t2, usec)
    return code

def generate_delay_list():
    trigger = 'u.sequence'
    t_range = ['1000', '1100']
    usec = range(1, 1000)
    code = []
    for u in usec:
        code.append(_generate_delay_code(trigger, t_range[0], t_range[1], u))
    return code

def generate_stuck_fault_list():
    trigger = 'u.sequence'
    t_range = ['1000', '1100']
    code = []
    variable = [ \
            ['u.delay[0]', 'u.delay[1]'], \
            ['u.grasp[0]','u.grasp[1]'] \
            ]
    stuck_val = [ \
            ['100','110'], \
            ['20','30']
            ]
    for v, s in zip(variable, stuck_val):
        code.append(_generate_ow_code(trigger, \
                t_range[0], t_range[1], v, s))
    return code

def run():
    # Generate code
    code = generate_delay_list()

    # Write code to file
    with open('mfi2.txt', 'w') as outfile:
        outfile.writelines('location:network_layer.cpp://MFI_HOOK\n')
        for i, line in enumerate(code):
            outfile.writelines('injection %d:%s\n' % (i,line))

#print generate_add_code('u.sequence', '1000', '1100', ['u.delay[0]','hello'], ['100','11'])
#pprint(generate_delay_list())
#pprint(generate_stuck_fault_list())

run()
