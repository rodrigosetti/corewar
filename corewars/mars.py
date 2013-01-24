# coding: utf-8

from copy import copy
from random import randint
from core import Core, DEFAULT_INITIAL_INSTRUCTION
from redcode import *

__all__ = ['MARS']

class MARS(object):
    """The MARS. Encapsulates a simulation.
    """

    def __init__(self, core=None, warriors=None, minimum_separation=100):
        self.core = core if core else Core()
        self.task_queue = []
        self.minimum_separation = minimum_separation
        self.warriors = warriors if warriors else []
        if self.warriors:
            self.load_warriors()

    def reset(self, clear_instruction=DEFAULT_INITIAL_INSTRUCTION):
        "Clears core and re-loads warriors."
        self.core.clear(clear_instruction)
        self.load_warriors()

    def load_warriors(self):
        "Loads its warriors to the memory with starting task queues"

        # the space between warriors - equally spaced in the core
        space = len(self.core) / len(self.warriors)

        for n, warrior in enumerate(self.warriors):
            # position is in the nth equally separated space plus a random
            # shift up to where the last instruction is minimum separated from
            # the first instruction of the next warrior
            start_position = (n * space) + randint(0, max(0, space -
                                                             len(warrior) -
                                                             self.minimum_separation))
            # add first and unique warrior task
            warrior.task_queue = [self.core.trim(start_position)]

            # copy warrior's instructions to the core
            for i, instruction in enumerate(warrior.instructions):
                self.core[start_position + i] = copy(instruction)

    def enqueue(self, warrior, address):
        warrior.task_queue.append(self.core.trim(address))

    def step(self):
        """Run one simulation step: execute one task of every active warrior.
        """
        for warrior in self.warriors:
            if warrior.task_queue:
                # The process counter is the next instruction-address in the
                # warrior's task queue
                pc = warrior.task_queue.pop(0)

                # copy the current instruction to the instruction register
                ir = copy(self.core[pc])

                # evaluate the A-operand
                if ir.a_mode == IMMEDIATE:
                    # if the mode is immediate, reading and writing a-pointers
                    # are zero
                    rpa = wpa = 0

                else:
                    # not immediate: direct or one of the indirect modes
                    rpa = self.core.trim_read(ir.a_number)
                    wpa = self.core.trim_write(ir.a_number)

                    if ir.a_mode != DIRECT:
                        # one of the indirect modes

                        # save this in case we need to use to post-increment
                        pip = (pc + wpa) % len(self.core)

                        # pre-decrement, if needed
                        if ir.a_mode == PREDEC_A:
                            self.core[pc + wpa].a_number -= 1
                        elif ir.a_mode == PREDEC_B:
                            self.core[pc + wpa].b_number -= 1

                        # calculate the indirect address, from A or B number
                        if ir.a_mode in (PREDEC_A, INDIRECT_A, POSTINC_A):
                            rpa = self.core.trim_read(rpa + self.core[pc + rpa].a_number)
                            wpa = self.core.trim_write(wpa + self.core[pc + rpa].a_number)
                        else:
                            rpa = self.core.trim_read(rpa + self.core[pc + rpa].b_number)
                            wpa = self.core.trim_write(wpa + self.core[pc + rpa].b_number)

                        # post-increment, if needed
                        if ir.a_mode == POSTINC_A:
                            self.core[pip].a_number += 1
                        elif ir.a_mode == POSTINC_B:
                            self.core[pip].b_number += 1

                # copy instruction pointer by A
                ira = copy(self.core[pc + rpa])

                # evaluate the B-operand - pretty much the same as A
                if ir.b_mode == IMMEDIATE:
                    rpb = wpb = 0
                else:
                    rpb = self.core.trim_read(ir.b_number)
                    wpb = self.core.trim_write(ir.b_number)

                    if ir.b_mode != DIRECT:
                        pip = (pc + wpb) % len(self.core)

                        if ir.b_mode == PREDEC_A:
                            self.core[pc + wpb].a_number -= 1
                        elif ir.b_mode == PREDEC_B:
                            self.core[pc + wpb].b_number -= 1

                        if ir.b_mode in (PREDEC_A, INDIRECT_A, POSTINC_A):
                            rpb = self.core.trim_read(rpb + self.core[pc + rpb].a_number)
                            wpb = self.core.trim_write(wpb + self.core[pc + rpb].a_number)
                        else:
                            rpb = self.core.trim_read(rpb + self.core[pc + rpb].b_number)
                            wpb = self.core.trim_write(wpb + self.core[pc + rpb].b_number)

                        if ir.b_mode == POSTINC_A:
                            self.core[pip].a_number += 1
                        elif ir.b_mode == POSTINC_B:
                            self.core[pip].b_number += 1

                irb = copy(self.core[pc + rpb])

                if ir.opcode == DAT:
                    # does not enqueue next instruction, therefore, killing the
                    # process
                    pass
                elif ir.opcode == MOV:
                    if ir.modifier == M_A:
                        self.core[pc + wpb].a_number = ira.a_number
                    elif ir.modifier == M_B:
                        self.core[pc + wpb].b_number = ira.b_number
                    elif ir.modifier == M_AB:
                        self.core[pc + wpb].b_number = ira.a_number
                    elif ir.modifier == M_BA:
                        self.core[pc + wpb].a_number = ira.b_number
                    elif ir.modifier == M_F:
                        self.core[pc + wpb].a_number = ira.a_number
                        self.core[pc + wpb].b_number = ira.b_number
                    elif ir.modifier == M_X:
                        self.core[pc + wpb].b_number = ira.a_number
                        self.core[pc + wpb].a_number = ira.b_number
                    elif ir.modifier == M_I:
                        self.core[pc + wpb] = ira
                    else:
                        raise ValueError("Invalid modifier: %d" % ir.modifier)

                    # enqueue next instruction
                    self.enqueue(warrior, pc + 1)
                elif ir.opcode == ADD:
                    # TODO: The rest of opcodes
                    pass
                elif ir.opcode == SUB:
                    pass
                elif ir.opcode == MUL:
                    pass
                elif ir.opcode == DIV:
                    pass
                elif ir.opcode == MOD:
                    pass
                elif ir.opcode == JMP:
                    pass
                elif ir.opcode == JMZ:
                    pass
                elif ir.opcode == JMN:
                    pass
                elif ir.opcode == DJN:
                    pass
                elif ir.opcode == SPL:
                    pass
                elif ir.opcode == SLT:
                    pass
                elif ir.opcode == CMP:
                    pass
                elif ir.opcode == SEQ:
                    pass
                elif ir.opcode == SNE:
                    pass
                elif ir.opcode == NOP:
                    pass
                elif ir.opcode == LDP:
                    pass
                elif ir.opcode == STP:
                    pass
                else:
                    raise ValueError("Invalid opcode: %d" % ir.opcode)


