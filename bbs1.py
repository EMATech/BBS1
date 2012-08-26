#!/usr/bin/env python2
from pygame import midi
import re

# Messages in readable format
init = [0xF0, 0x00, 0x40, 0x70, 0x01, 0x02, 0x00, 0x20, 0x00, 0x00, 0x00, 0x00,
    0xF7]
mode = [0xF0, 0x00, 0x40, 0x70, 0x01, 0x02, 0x00, 0x22, 0x00, 0x00, 0x00, 0x00,
    0xF7]
version = [0xF0, 0x00, 0x40, 0x70, 0x01, 0x02, 0x00, 0x15, 0x00, 0x00, 0x00,
    0x00, 0xF7]

# Initialize Pygame's MIDI
midi.init()

# Get MIDI devices
devices = midi.get_count()

# Search first BodyBeatSync input and output ports
for i in range(0, devices):
    info = midi.get_device_info(i)
    if(re.match('.*BodyBeatSYNC MIDI 1.*', str(info[1]))):
        if(info[2] >= 1):
            dev_in = i
        if(info[3] >= 1):
            dev_out = i

# Let's check if we got something
try:
    dev_in
except NameError:
    print "Couldn't find BodyBeatSync's input port"
    exit()

try:
    dev_out
except NameError:
    print "Couldn't find BodyBeatSync's output port"
    exit()

# Open input and output
midi_in = midi.Input(dev_in)
midi_out = midi.Output(dev_out)


def get_data(msg):
    '''Get data'''
    # Send out SysEx
    midi_out.write_sys_ex(0, msg)

    # Wait for answer
    while not midi_in.poll():
        pass

    # Read answer
    answer = list()
    while midi_in.poll():
        raw_answer = midi_in.read(1)
        for event in raw_answer:
            for data in event[0]:
                answer.append(data)
                # Strip remaining data after sysex end
                if data == 0xF7:
                    break

    #TODO Check answer

    return answer


def present():
    return get_data(init)

def get_mode():
    return get_data(mode)


def get_version():
    raw_version = get_data(version)
    readable_version = str(raw_version[12]) + '.'\
        + str(raw_version[14]) + '.' + str(raw_version[16])
    return readable_version

print present()
print get_mode()
print get_version()
