#! /usr/bin/env python
# coding: utf-8

from copy import copy
import operator
from random import randint

from core import Core, DEFAULT_INITIAL_INSTRUCTION
from redcode import *

__all__ = ['MARS', 'EVENT_EXECUTED' 'EVENT_I_WRITE', 'EVENT_I_READ',
           'EVENT_A_DEC', 'EVENT_A_INC', 'EVENT_B_DEC', 'EVENT_B_INC',
           'EVENT_A_READ', 'EVENT_A_WRITE', 'EVENT_B_READ', 'EVENT_B_WRITE',
           'EVENT_A_ARITH', 'EVENT_B_ARITH']

# Event types
EVENT_EXECUTED = 0
EVENT_I_WRITE  = 1
EVENT_I_READ   = 2
EVENT_A_DEC    = 3
EVENT_A_INC    = 4
EVENT_B_DEC    = 5
EVENT_B_INC    = 6
EVENT_A_READ   = 7
EVENT_A_WRITE  = 8
EVENT_B_READ   = 9
EVENT_B_WRITE  = 10
EVENT_A_ARITH  = 11
EVENT_B_ARITH  = 12

class MARS(object):
    """The MARS. Encapsulates a simulation.
    """

    def __init__(self, core=None, warriors=None, minimum_separation=100,
                 randomize=True, max_processes=None):
        self.core = core if core else Core()
        self.minimum_separation = minimum_separation
        self.max_processes = max_processes if max_processes else len(self.core)
        self.warriors = warriors if warriors else []
        if self.warriors:
            self.load_warriors(randomize)

    def core_event(self, warrior, address, event_type):
        """Supposed to be implemented by subclasses to handle core
           events.
        """
        pass

    def reset(self, clear_instruction=DEFAULT_INITIAL_INSTRUCTION):
        "Clears core and re-loads warriors."
        self.core.clear(clear_instruction)
        self.load_warriors()

    def load_warriors(self, randomize=True):
        "Loads its warriors to the memory with starting task queues"

        # the space between warriors - equally spaced in the core
        space = len(self.core) / len(self.warriors)

        for n, warrior in enumerate(self.warriors):
            # position is in the nth equally separated space plus a random
            # shift up to where the last instruction is minimum separated from
            # the first instruction of the next warrior
            warrior_position = (n * space)

            if randomize:
                warrior_position += randint(0, max(0, space -
                                                      len(warrior) -
                                                      self.minimum_separation))

            # add first and unique warrior task
            warrior.task_queue = [self.core.trim(warrior_position + warrior.start)]

            # copy warrior's instructions to the core
            for i, instruction in enumerate(warrior.instructions):
                self.core[warrior_position + i] = copy(instruction)

    def enqueue(self, warrior, address):
        """Enqueue another process into the warrior's task queue. Only if it's
           not already full.
        """
        if len(warrior.task_queue) < self.max_processes:
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
                        pip = pc + wpa

                        # pre-decrement, if needed
                        if ir.a_mode == PREDEC_A:
                            self.core[pc + wpa].a_number -= 1
                            self.core_event(warrior, pc + wpa, EVENT_A_DEC)
                        elif ir.a_mode == PREDEC_B:
                            self.core[pc + wpa].b_number -= 1
                            self.core_event(warrior, pc + wpa, EVENT_B_DEC)

                        # calculate the indirect address, from A or B number
                        if ir.a_mode in (PREDEC_A, INDIRECT_A, POSTINC_A):
                            rpa = self.core.trim_read(rpa + self.core[pc + rpa].a_number)
                            wpa = self.core.trim_write(wpa + self.core[pc + wpa].a_number)
                        else:
                            rpa = self.core.trim_read(rpa + self.core[pc + rpa].b_number)
                            wpa = self.core.trim_write(wpa + self.core[pc + wpa].b_number)

                # copy instruction pointer by A
                ira = copy(self.core[pc + rpa])

                # post-increment, if needed
                if ir.a_mode == POSTINC_A:
                    self.core[pip].a_number += 1
                    self.core_event(warrior, pip, EVENT_A_INC)
                elif ir.a_mode == POSTINC_B:
                    self.core[pip].b_number += 1
                    self.core_event(warrior, pip, EVENT_B_INC)

                # evaluate the B-operand - pretty much the same as A
                if ir.b_mode == IMMEDIATE:
                    rpb = wpb = 0
                else:
                    rpb = self.core.trim_read(ir.b_number)
                    wpb = self.core.trim_write(ir.b_number)

                    if ir.b_mode != DIRECT:
                        pip = pc + wpb

                        if ir.b_mode == PREDEC_A:
                            self.core[pc + wpb].a_number -= 1
                            self.core_event(warrior, pc + wpb, EVENT_A_DEC)
                        elif ir.b_mode == PREDEC_B:
                            self.core[pc + wpb].b_number -= 1
                            self.core_event(warrior, pc + wpb, EVENT_B_DEC)

                        if ir.b_mode in (PREDEC_A, INDIRECT_A, POSTINC_A):
                            rpb = self.core.trim_read(rpb + self.core[pc + rpb].a_number)
                            wpb = self.core.trim_write(wpb + self.core[pc + wpb].a_number)
                        else:
                            rpb = self.core.trim_read(rpb + self.core[pc + rpb].b_number)
                            wpb = self.core.trim_write(wpb + self.core[pc + wpb].b_number)

                irb = copy(self.core[pc + rpb])

                if ir.b_mode == POSTINC_A:
                    self.core[pip].a_number += 1
                    self.core_event(warrior, pip, EVENT_A_INC)
                elif ir.b_mode == POSTINC_B:
                    self.core[pip].b_number += 1
                    self.core_event(warrior, pip, EVENT_B_INC)

                # arithmetic common code
                def do_arithmetic(op):
                    try:
                        if ir.modifier == M_A:
                            self.core[pc + wpb].a_number = op(irb.a_number, ira.a_number)
                            self.core_event(warrior, pc + wpb, EVENT_A_WRITE)
                            self.core_event(warrior, pc + rpa, EVENT_A_READ)
                            self.core_event(warrior, pc + rpb, EVENT_A_READ)
                        elif ir.modifier == M_B:
                            self.core[pc + wpb].b_number = op(irb.b_number, ira.b_number)
                            self.core_event(warrior, pc + wpb, EVENT_B_WRITE)
                            self.core_event(warrior, pc + rpa, EVENT_B_READ)
                            self.core_event(warrior, pc + rpb, EVENT_B_READ)
                        elif ir.modifier == M_AB:
                            self.core[pc + wpb].b_number = op(irb.b_number, ira.a_number)
                            self.core_event(warrior, pc + wpb, EVENT_B_WRITE)
                            self.core_event(warrior, pc + rpa, EVENT_A_READ)
                            self.core_event(warrior, pc + rpb, EVENT_B_READ)
                        elif ir.modifier == M_BA:
                            self.core[pc + wpb].a_number = op(irb.b_number, ira.a_number)
                            self.core_event(warrior, pc + wpb, EVENT_A_WRITE)
                            self.core_event(warrior, pc + rpa, EVENT_A_READ)
                            self.core_event(warrior, pc + rpb, EVENT_B_READ)
                        elif ir.modifier == M_F or ir.modifier == M_I:
                            self.core[pc + wpb].a_number = op(irb.a_number, ira.a_number)
                            self.core[pc + wpb].b_number = op(irb.b_number, ira.b_number)
                            self.core_event(warrior, pc + wpb, EVENT_A_WRITE)
                            self.core_event(warrior, pc + wpb, EVENT_B_WRITE)
                            self.core_event(warrior, pc + rpa, EVENT_A_READ)
                            self.core_event(warrior, pc + rpb, EVENT_A_READ)
                            self.core_event(warrior, pc + rpa, EVENT_B_READ)
                            self.core_event(warrior, pc + rpb, EVENT_B_READ)
                        elif ir.modifier == M_X:
                            self.core[pc + wpb].b_number = op(irb.b_number, ira.a_number)
                            self.core[pc + wpb].a_number = op(irb.a_number, ira.b_number)
                            self.core_event(warrior, pc + wpb, EVENT_A_WRITE)
                            self.core_event(warrior, pc + wpb, EVENT_B_WRITE)
                            self.core_event(warrior, pc + rpa, EVENT_A_READ)
                            self.core_event(warrior, pc + rpb, EVENT_A_READ)
                            self.core_event(warrior, pc + rpa, EVENT_B_READ)
                            self.core_event(warrior, pc + rpb, EVENT_B_READ)
                        else:
                            raise ValueError("Invalid modifier: %d" % ir.modifier)

                        # enqueue next instruction
                        self.enqueue(warrior, pc + 1)
                    except ZeroDivisionError:
                        pass

                # comparison common code
                def do_comparison(cmp):
                    if ir.modifier == M_A:
                        self.enqueue(warrior,
                                     pc + (2 if cmp(ira.a_number, irb.a_number) else 1))
                        self.core_event(warrior, pc + rpa, EVENT_A_READ)
                        self.core_event(warrior, pc + rpb, EVENT_A_READ)
                    elif ir.modifier == M_B:
                        self.enqueue(warrior,
                                     pc + (2 if cmp(ira.b_number, irb.b_number) else 1))
                        self.core_event(warrior, pc + rpa, EVENT_B_READ)
                        self.core_event(warrior, pc + rpb, EVENT_B_READ)
                    elif ir.modifier == M_AB:
                        self.enqueue(warrior,
                                     pc + (2 if cmp(ira.a_number, irb.b_number) else 1))
                        self.core_event(warrior, pc + rpa, EVENT_A_READ)
                        self.core_event(warrior, pc + rpb, EVENT_B_READ)
                    elif ir.modifier == M_BA:
                        self.enqueue(warrior,
                                     pc + (2 if cmp(ira.b_number, irb.a_number) else 1))
                        self.core_event(warrior, pc + rpa, EVENT_B_READ)
                        self.core_event(warrior, pc + rpb, EVENT_A_READ)
                    elif ir.modifier == M_F:
                        self.enqueue(warrior,
                                     pc + (2 if cmp(ira.a_number, irb.a_number) and
                                                cmp(ira.b_number, irb.b_number) else 1))
                        self.core_event(warrior, pc + rpa, EVENT_A_READ)
                        self.core_event(warrior, pc + rpb, EVENT_A_READ)
                        self.core_event(warrior, pc + rpa, EVENT_B_READ)
                        self.core_event(warrior, pc + rpb, EVENT_B_READ)
                    elif ir.modifier == M_X:
                        self.enqueue(warrior,
                                     pc + (2 if cmp(ira.a_number, irb.b_number) and
                                                cmp(ira.b_number, irb.a_number) else 1))
                        self.core_event(warrior, pc + rpa, EVENT_A_READ)
                        self.core_event(warrior, pc + rpb, EVENT_A_READ)
                        self.core_event(warrior, pc + rpa, EVENT_B_READ)
                        self.core_event(warrior, pc + rpb, EVENT_B_READ)
                    elif ir.modifier == M_I:
                        self.enqueue(warrior,
                                     pc + (2 if ira == irb else 1))
                        self.core_event(warrior, pc + rpa, EVENT_I_READ)
                        self.core_event(warrior, pc + rpb, EVENT_I_READ)
                    else:
                        raise ValueError("Invalid modifier: %d" % ir.modifier)

                self.core_event(warrior, pc, EVENT_EXECUTED)

                if ir.opcode == DAT:
                    # does not enqueue next instruction, therefore, killing the
                    # process
                    pass
                elif ir.opcode == MOV:
                    if ir.modifier == M_A:
                        self.core[pc + wpb].a_number = ira.a_number
                        self.core_event(warrior, pc + rpa, EVENT_A_READ)
                        self.core_event(warrior, pc + wpb, EVENT_A_WRITE)
                    elif ir.modifier == M_B:
                        self.core[pc + wpb].b_number = ira.b_number
                        self.core_event(warrior, pc + rpa, EVENT_B_READ)
                        self.core_event(warrior, pc + wpb, EVENT_B_WRITE)
                    elif ir.modifier == M_AB:
                        self.core[pc + wpb].b_number = ira.a_number
                        self.core_event(warrior, pc + rpa, EVENT_A_READ)
                        self.core_event(warrior, pc + wpb, EVENT_B_WRITE)
                    elif ir.modifier == M_BA:
                        self.core[pc + wpb].a_number = ira.b_number
                        self.core_event(warrior, pc + rpa, EVENT_B_READ)
                        self.core_event(warrior, pc + wpb, EVENT_A_WRITE)
                    elif ir.modifier == M_F:
                        self.core[pc + wpb].a_number = ira.a_number
                        self.core[pc + wpb].b_number = ira.b_number
                        self.core_event(warrior, pc + rpa, EVENT_A_READ)
                        self.core_event(warrior, pc + rpa, EVENT_B_READ)
                        self.core_event(warrior, pc + wpb, EVENT_A_WRITE)
                        self.core_event(warrior, pc + wpb, EVENT_B_WRITE)
                    elif ir.modifier == M_X:
                        self.core[pc + wpb].b_number = ira.a_number
                        self.core[pc + wpb].a_number = ira.b_number
                        self.core_event(warrior, pc + rpa, EVENT_A_READ)
                        self.core_event(warrior, pc + rpa, EVENT_B_READ)
                        self.core_event(warrior, pc + wpb, EVENT_A_WRITE)
                        self.core_event(warrior, pc + wpb, EVENT_B_WRITE)
                    elif ir.modifier == M_I:
                        self.core[pc + wpb] = ira
                        self.core_event(warrior, pc + rpa, EVENT_I_READ)
                        self.core_event(warrior, pc + wpb, EVENT_I_WRITE)
                    else:
                        raise ValueError("Invalid modifier: %d" % ir.modifier)

                    # enqueue next instruction
                    self.enqueue(warrior, pc + 1)
                elif ir.opcode == ADD:
                    do_arithmetic(operator.add)
                elif ir.opcode == SUB:
                    do_arithmetic(operator.sub)
                elif ir.opcode == MUL:
                    do_arithmetic(operator.mul)
                elif ir.opcode == DIV:
                    do_arithmetic(operator.div)
                elif ir.opcode == MOD:
                    do_arithmetic(operator.mod)
                elif ir.opcode == JMP:
                    self.enqueue(warrior, pc + rpa)
                elif ir.opcode == JMZ:
                    if ir.modifier == M_A or ir.modifier == M_BA:
                        self.enqueue(warrior, pc + (rpa if irb.a_number == 0 else 1))
                        self.core_event(warrior, pc + rpa, EVENT_A_READ)
                    elif ir.modifier == M_B or ir.modifier == M_AB:
                        self.enqueue(warrior, pc + (rpa if irb.b_number == 0 else 1))
                        self.core_event(warrior, pc + rpa, EVENT_B_READ)
                    elif ir.modifier in (M_F, M_X, M_I):
                        self.enqueue(warrior,
                                     pc + (rpa if irb.a_number == irb.b_number == 0 else 1))
                        self.core_event(warrior, pc + rpa, EVENT_A_READ)
                        self.core_event(warrior, pc + rpa, EVENT_B_READ)
                    else:
                        raise ValueError("Invalid modifier: %d" % ir.modifier)
                elif ir.opcode == JMN:
                    if ir.modifier == M_A or ir.modifier == M_BA:
                        self.enqueue(warrior, pc + (rpa if irb.a_number != 0 else 1))
                        self.core_event(warrior, pc + rpa, EVENT_A_READ)
                    elif ir.modifier == M_B or ir.modifier == M_AB:
                        self.enqueue(warrior, pc + (rpa if irb.b_number != 0 else 1))
                        self.core_event(warrior, pc + rpa, EVENT_B_READ)
                    elif ir.modifier in (M_F, M_X, M_I):
                        self.enqueue(warrior,
                                     pc + (rpa if irb.a_number != 0 or
                                                  irb.b_number != 0 else 1))
                        self.core_event(warrior, pc + rpa, EVENT_A_READ)
                        self.core_event(warrior, pc + rpa, EVENT_B_READ)
                    else:
                        raise ValueError("Invalid modifier: %d" % ir.modifier)
                elif ir.opcode == DJN:
                    if ir.modifier == M_A or ir.modifier == M_BA:
                        self.core[pc + wpb].a_number -= 1
                        irb.a_number -= 1
                        self.enqueue(warrior, pc + (rpa if irb.a_number != 0 else 1))
                        self.core_event(warrior, pc + rpa, EVENT_A_READ)
                        self.core_event(warrior, pc + rpa, EVENT_A_DEC)
                    elif ir.modifier == M_B or ir.modifier == M_AB:
                        self.core[pc + wpb].b_number -= 1
                        irb.b_number -= 1
                        self.enqueue(warrior, pc + (rpa if irb.b_number != 0 else 1))
                        self.core_event(warrior, pc + rpa, EVENT_B_READ)
                        self.core_event(warrior, pc + rpa, EVENT_B_DEC)
                    elif ir.modifier in (M_F, M_X, M_I):
                        self.core[pc + wpb].a_number -= 1
                        irb.a_number -= 1
                        self.core[pc + wpb].b_number -= 1
                        irb.b_number -= 1
                        self.enqueue(warrior,
                                     pc + (rpa if irb.a_number != 0 or
                                                  irb.b_number != 0 else 1))
                        self.core_event(warrior, pc + rpa, EVENT_A_READ)
                        self.core_event(warrior, pc + rpa, EVENT_B_READ)
                        self.core_event(warrior, pc + rpa, EVENT_A_DEC)
                        self.core_event(warrior, pc + rpa, EVENT_B_DEC)
                    else:
                        raise ValueError("Invalid modifier: %d" % ir.modifier)
                elif ir.opcode == SPL:
                    self.enqueue(warrior, pc + 1)
                    self.enqueue(warrior, pc + rpa)
                elif ir.opcode == SLT:
                    do_comparison(operator.lt)
                elif ir.opcode == CMP or ir.opcode == SEQ:
                    do_comparison(operator.eq)
                elif ir.opcode == SNE:
                    do_comparison(operator.ne)
                elif ir.opcode == NOP:
                    self.enqueue(warrior, pc + 1)
                else:
                    raise ValueError("Invalid opcode: %d" % ir.opcode)

if __name__ == "__main__":
    import argparse
    import redcode

    parser = argparse.ArgumentParser(description='MARS (Memory Array Redcode Simulator)')
    parser.add_argument('--rounds', '-r', metavar='ROUNDS', type=int, nargs='?',
                        default=1, help='Rounds to play')
    parser.add_argument('--size', '-s', metavar='CORESIZE', type=int, nargs='?',
                        default=8000, help='The core size')
    parser.add_argument('--cycles', '-c', metavar='CYCLES', type=int, nargs='?',
                        default=80000, help='Cycles until tie')
    parser.add_argument('--processes', '-p', metavar='MAXPROCESSES', type=int, nargs='?',
                        default=8000, help='Max processes')
    parser.add_argument('--length', '-l', metavar='MAXLENGTH', type=int, nargs='?',
                        default=100, help='Max warrior length')
    parser.add_argument('--distance', '-d', metavar='MINDISTANCE', type=int, nargs='?',
                        default=100, help='Minimum warrior distance')
    parser.add_argument('warriors', metavar='WARRIOR', type=str, nargs='+',
                        help='Warrior redcode filename')

    args = parser.parse_args()

    # build environment
    environment = {'CORESIZE': args.size,
                   'CYCLES': args.cycles,
                   'ROUNDS': args.rounds,
                   'MAXPROCESSES': args.processes,
                   'MAXLENGTH': args.length,
                   'MINDISTANCE': args.distance}

    # assemble warriors
    warriors = [redcode.parse(open(filename), environment) for filename in args.warriors]

    # initialize wins, losses and ties for each warrior
    for warrior in warriors:
        warrior.wins = warrior.ties = warrior.losses = 0

    # for each round
    for i in xrange(args.rounds):

        # create new simulation
        simulation = MARS(warriors=warriors,
                          minimum_separation = args.distance,
                          max_processes = args.processes)

        active_warrior_to_stop = 1 if len(warriors) >= 2 else 0

        for c in xrange(args.cycles):
            simulation.step()

            # if there's only one left, or are all dead, then stop simulation
            if sum(1 if warrior.task_queue else 0 for warrior in warriors) <= active_warrior_to_stop:
                for warrior in warriors:
                    if warrior.task_queue:
                        warrior.wins += 1
                    else:
                        warrior.losses += 1
                break
        else:
            # running until max cycles: tie
            for warrior in warriors:
                if warrior.task_queue:
                    warrior.ties += 1
                else:
                    warrior.losses += 1

    # print results
    print "Results: (%d rounds)" % args.rounds
    print "%s %s %s %s" % ("Warrior (Author)".ljust(30), "wins".rjust(5),
                           "ties".rjust(5), "losses".rjust(5))
    for warrior in warriors:
        print "%s %s %s %s" % (("%s (%s)" % (warrior.name, warrior.author)).ljust(30),
                               str(warrior.wins).rjust(5),
                               str(warrior.ties).rjust(5),
                               str(warrior.losses).rjust(5))


