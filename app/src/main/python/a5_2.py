# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
Created on Thu Oct 8 17:06:49 2020

@author: OUCHATTI-Khadija
"""


from lfsr import LFSR
from BitVector import BitVector
import copy
from constant import *
import math


class A5_2(object):
    def __init__(self, key, frame_counter):

        if not (key >= 0 and key < math.pow(2, KEY_SIZE)):
            raise ValueError('Key value must be between 0 and 2^64!')
        if not (frame_counter >= 0 and frame_counter < math.pow(2, FRAME_COUNTER_SIZE)):
            raise ValueError('Frame counter value must be between 0 and 2^22!')
        self.r1 = LFSR(R1_SIZE, [], R1_TAPS, R1_MAJORITY_BITS, R1_NEGATED_BIT)
        self.r2 = LFSR(R2_SIZE, [], R2_TAPS, R2_MAJORITY_BITS, R2_NEGATED_BIT)
        self.r3 = LFSR(R3_SIZE, [], R3_TAPS, R3_MAJORITY_BITS, R3_NEGATED_BIT)
        self.r4 = LFSR(R4_SIZE, R4_CLOCK_BITS, R4_TAPS, [], None)
        self.key = BitVector(size=KEY_SIZE, intVal=key)
        self.frame_counter = BitVector(size=FRAME_COUNTER_SIZE,
                                       intVal=frame_counter)
        self.key_stream = BitVector(size=KEY_STREAM_SIZE)
        self.register_states = []

    def get_key_stream_with_predefined_registers(self, r1, r2, r3, r4, generate_only_send_key=False):

        self.r1 = LFSR(R1_SIZE, [], R1_TAPS, R1_MAJORITY_BITS, R1_NEGATED_BIT, bitstring=r1)
        self.r2 = LFSR(R2_SIZE, [], R2_TAPS, R2_MAJORITY_BITS, R2_NEGATED_BIT, bitstring=r2)
        self.r3 = LFSR(R3_SIZE, [], R3_TAPS, R3_MAJORITY_BITS, R3_NEGATED_BIT, bitstring=r3)
        self.r4 = LFSR(R4_SIZE, R4_CLOCK_BITS, R4_TAPS, [], None, bitstring=r4)

        self._clocking_with_majority(MAJORITY_CYCLES_A52)
        self._generate_key_stream(generate_only_send_key=generate_only_send_key)
        return (self.send_key, self.receive_key)

    def _create_register_backup(self):

        self.initial_sates = {'r1': copy.deepcopy(self.r1),
                              'r2': copy.deepcopy(self.r2),
                              'r3': copy.deepcopy(self.r3),
                              'r4': copy.deepcopy(self.r4)}

    def _set_bits(self):

        self.r1.set_bit(FORCE_R1_BIT_TO_1, 1)
        self.r2.set_bit(FORCE_R2_BIT_TO_1, 1)
        self.r3.set_bit(FORCE_R3_BIT_TO_1, 1)
        self.r4.set_bit(FORCE_R4_BIT_TO_1, 1)

    def _clocking(self, limit, vector):

        for i in reversed(range(limit)):
            self.r1.clock(vector[i])
            self.r2.clock(vector[i])
            self.r3.clock(vector[i])
            self.r4.clock(vector[i])

    def _clocking_with_majority(self, limit, generate_key_stream=False, save_register_states=False):

        for i in range(limit):
            majority = self._majority()
            if self.r4.get_bit(R4_CLOCKING_BIT_FOR_R1) == majority:
                self.r1.clock()
            if self.r4.get_bit(R4_CLOCKING_BIT_FOR_R2) == majority:
                self.r2.clock()
            if self.r4.get_bit(R4_CLOCKING_BIT_FOR_R3) == majority:
                self.r3.clock()
            self.r4.clock()
            if generate_key_stream:
                if save_register_states:
                    self.register_states.append({'r1': copy.deepcopy(self.r1),
                                                 'r2': copy.deepcopy(self.r2),
                                                 'r3': copy.deepcopy(self.r3)})
                self._add_key_stream_bit(i)

    def _generate_key_stream(self, save_register_states=False, generate_only_send_key=False):

        self._clocking_with_majority(KEY_STREAM_SIZE, save_register_states=save_register_states, generate_key_stream=True)
        if not generate_only_send_key:
            self.send_key = self.key_stream.deep_copy()
            self._clocking_with_majority(KEY_STREAM_SIZE, save_register_states=save_register_states, generate_key_stream=True)
            self.receive_key = self.key_stream.deep_copy()
        else:
            self.send_key = self.key_stream
            self.receive_key = None

    def get_key_stream(self, save_register_states=False, generate_only_send_key=False):
        
        self._clocking(KEY_SIZE, self.key)
        self._clocking(FRAME_COUNTER_SIZE, self.frame_counter)
        self._set_bits()
        self._create_register_backup()
        self._clocking_with_majority(MAJORITY_CYCLES_A52)
        self._generate_key_stream(save_register_states, generate_only_send_key=generate_only_send_key)

        return (self.send_key, self.receive_key)

    def _add_key_stream_bit(self, index):

        self.key_stream[index] = self.r1.register[0] ^ self.r2.register[0] ^ self.r3.register[0] ^ self.r1.get_majority() ^ self.r2.get_majority() ^ self.r3.get_majority()

    def _majority(self):
    
        clocked_bits = []
        clocked_bits = clocked_bits + self.r4.get_clock_bits()
        a = clocked_bits[0]
        b = clocked_bits[1]
        c = clocked_bits[2]
        return (a*b) ^ (a*c) ^ (b*c) 
