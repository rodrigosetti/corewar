#! /usr/bin/env python
# coding: utf-8

import pygame
from pygame.locals import *

from core import DEFAULT_INITIAL_INSTRUCTION
from mars import *
from redcode import *

#: Opcode to ASCII for drawing
OPCODES_ASCII = {'DAT': 'D', 'MOV': 'M', 'ADD': '+', 'SUB': '-', 'MUL': '*',
                 'DIV': '/', 'MOD': '%', 'JMP': 'J', 'JMZ': 'Z', 'JMN': 'N',
                 'DJN': 'n', 'SPL': 'S', 'SLT': '<', 'CMP': '=', 'SEQ': '=',
                 'SNE': '!', 'NOP': ';'}

INSTRUCTIONS_PER_LINE = 100
INSTRUCTION_SIZE_X = 10
INSTRUCTION_SIZE_Y = 10

I_AREA = ((0,0), (INSTRUCTION_SIZE_X, INSTRUCTION_SIZE_Y))

# initialize pygame engine
pygame.init()

CORE_FONT = pygame.font.SysFont("monospace", INSTRUCTION_SIZE_X-1)
OPCODE_GLIPHS = {
    DAT: 'D',
    MOV: 'M',
    ADD: '+',
    SUB: '-',
    MUL: '*',
    DIV: '/',
    MOD: '%',
    JMP: 'J',
    JMZ: 'Z',
    JMN: 'N',
    DJN: 'j',
    SPL: 'S',
    SLT: '<',
    CMP: '=',
    SEQ: '=',
    SNE: '!',
    NOP: ';'}

DEFAULT_FG_COLOR = (100,100,100)
WHITE = (255,255,255)
BLACK = (0, 0, 0)
DEFAULT_BG_COLOR = (0, 0, 0)

# Colors are dark and bright
WARRIOR_COLORS = (((0,0,100), (0,0,255)),
                  ((0,100,0), (0,255,0)),
                  ((0,100,100), (0,255,255)),
                  ((100,0,0), (255,0,0)),
                  ((100,0,100), (255,0,255)),
                  ((100,100,0), (255,255,0)))

class PygameMARS(MARS):

    def __init__(self, *args, **kargs):
        super(PygameMARS, self).__init__(*args, **kargs)
        self.size = (INSTRUCTION_SIZE_X * INSTRUCTIONS_PER_LINE,
                     INSTRUCTION_SIZE_Y * (len(self) / INSTRUCTIONS_PER_LINE))
        self.core_surface = pygame.Surface(self.size)
        self.recent_events = pygame.Surface(self.size)
        self.recent_events.set_colorkey(DEFAULT_BG_COLOR)

    def reset(self, clear_instruction=DEFAULT_INITIAL_INSTRUCTION):
        self.core.clear(clear_instruction)
        for n, instruction in enumerate(self):
            self.core_surface.blit(CORE_FONT.render(OPCODE_GLIPHS[instruction.opcode],
                                                    True, # anti-alias
                                                    DEFAULT_FG_COLOR,
                                                    DEFAULT_BG_COLOR),
                                   ((n % INSTRUCTIONS_PER_LINE) * INSTRUCTION_SIZE_X,
                                    (n / INSTRUCTIONS_PER_LINE) * INSTRUCTION_SIZE_Y))
        self.load_warriors()

    def step(self):
        self.recent_events.fill(DEFAULT_BG_COLOR)
        super(PygameMARS, self).step()

    def blit_into(self, surface, dest):
        surface.blit(self.core_surface, dest)
        surface.blit(self.recent_events, dest)

    def core_event(self, warrior, address, event_type):
        address %= len(self)
        position = ((address % INSTRUCTIONS_PER_LINE) * INSTRUCTION_SIZE_X,
                    (address / INSTRUCTIONS_PER_LINE) * INSTRUCTION_SIZE_Y)
        instruction = self.core[address]

        if event_type in (EVENT_I_WRITE, EVENT_A_WRITE, EVENT_B_WRITE):
            # In case of a write event, we write the foreground with the
            # warrior's color
            self.core_surface.blit(CORE_FONT.render(OPCODE_GLIPHS[instruction.opcode],
                                                    True,
                                                    warrior.color[1],
                                                    DEFAULT_BG_COLOR),
                                   position, area=I_AREA)
            self.recent_events.blit(CORE_FONT.render(OPCODE_GLIPHS[instruction.opcode],
                                                     True,
                                                     WHITE,
                                                     DEFAULT_BG_COLOR),
                                    position, area=I_AREA)
        elif event_type == EVENT_EXECUTED:
            # In case of execution, we write the background with warrior's color
            self.core_surface.blit(CORE_FONT.render(OPCODE_GLIPHS[instruction.opcode],
                                                    True,
                                                    WHITE,
                                                    warrior.color[0]),
                                   position, area=I_AREA)
            self.recent_events.blit(CORE_FONT.render(OPCODE_GLIPHS[instruction.opcode],
                                                     True,
                                                     BLACK,
                                                     warrior.color[1]),
                                    position, area=I_AREA)
        elif event_type in (EVENT_A_ARITH, EVENT_B_ARITH, EVENT_A_DEC,
                            EVENT_B_DEC, EVENT_A_INC, EVENT_B_INC):
            # In case of arithmetic modification, or increment/decrement, we
            # write a rectangle around the instruction
            pygame.draw.rect(self.core_surface, warrior.color[0],
                             (position, (INSTRUCTION_SIZE_X, INSTRUCTION_SIZE_Y)),
                              1)
            pygame.draw.rect(self.recent_events, warrior.color[1],
                             (position, (INSTRUCTION_SIZE_X, INSTRUCTION_SIZE_Y)),
                              1)


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='MARS (Memory Array Redcode Simulator)')
    parser.add_argument('--rounds', '-r', metavar='ROUNDS', type=int, nargs='?',
                        default=1, help='Rounds to play')
    parser.add_argument('--paused', action='store_true', default=False,
                        help='Start each round paused')
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
    parser.add_argument('warriors', metavar='WARRIOR', type=file, nargs='+',
                        help='Warrior redcode filename')

    args = parser.parse_args()

    # build environment
    environment = {'CORESIZE': args.size,
                   'CYCLES': args.cycles,
                   'ROUNDS': args.rounds,
                   'MAXPROCESSES': args.processes,
                   'MAXLENGTH': args.length,
                   'MINDISTANCE': args.distance}

    if len(args.warriors) > WARRIOR_COLORS:
        print >> sys.stderr, "Please specify a maximum of %d warriors." % len(WARRIOR_COLORS)
        sys.exit(1)

    # assemble warriors
    warriors = [parse(file, environment) for file in args.warriors]

    # initialize wins, losses, ties and color for each warrior
    for warrior, color in zip(warriors, WARRIOR_COLORS):
        warrior.wins = warrior.ties = warrior.losses = 0
        warrior.color = color

    # create MARS
    simulation = PygameMARS(minimum_separation = args.distance,
                            max_processes = args.processes)
    simulation.warriors = warriors

    # create display
    display_surface = pygame.display.set_mode(simulation.size)

    # control variables
    paused = False
    stop_rounds = False

    # create clock to control FPS
    clock = pygame.time.Clock()

    # for each round
    for round in xrange(1, args.rounds + 1):

        # reset simulation and load warriors
        simulation.reset()

        # start with all warriors active
        active_warriors = list(warriors)

        # how many warriors should be playing to skip to next round
        active_warrior_to_stop = 1 if len(warriors) >= 2 else 0

        # start paused if user requested from command line
        if args.paused:
            paused = True

        # control variable
        next_round = False

        print
        print "Starting round %d" % round

        for cycle in xrange(args.cycles):
            # step one simulation in MARS
            simulation.step()

            # blit MARS visualization into display
            simulation.blit_into(display_surface, (0,0))
            pygame.display.update()
            clock.tick(30)

            to_remove = []
            for warrior in active_warriors:
                if not warrior.task_queue:
                    print "%s (%s) losses after %d cycles." % (warrior.name,
                                                               warrior.author,
                                                               cycle)
                    warrior.losses += 1
                    to_remove.append(warrior)

            for warrior in to_remove:
                active_warriors.remove(warrior)

            # if there's only one left, or are all dead, then stop simulation
            if len(active_warriors) <= active_warrior_to_stop:
                for warrior in active_warriors:
                    print "%s (%s) wins after %d cycles." % (warrior.name,
                                                             warrior.author,
                                                             cycle)
                    warrior.wins += 1
                break

            step = False
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        # Tie all remaining bots and go to final results
                        next_round = True
                        stop_rounds = True
                        paused = False
                    elif event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            # toggle pausing
                            paused = not paused
                        elif event.key == K_s:
                            # step simulation (and pause)
                            paused = True
                            step = True
                        elif event.key == K_n:
                            # Tie all remaining bots and go to next round
                            next_round = True

                if not paused or step or next_round:
                    break

            if next_round:
                for warrior in active_warriors:
                    if warrior.task_queue:
                        print "%s (%s) ties after %d cycles." % (warrior.name,
                                                                 warrior.author,
                                                                 cycle)
                        warrior.ties += 1
                break
        else:
            # running until max cycles: tie
            for warrior in active_warriors:
                if warrior.task_queue:
                    print "%s (%s) ties after %d cycles." % (warrior.name,
                                                             warrior.author,
                                                             cycle)
                    warrior.ties += 1

        if stop_rounds:
            break

    # print final results
    print
    print "Final results: (%d rounds)" % round
    print "%s %s %s %s" % ("Warrior (Author)".ljust(40), "wins".rjust(5),
                           "ties".rjust(5), "losses".rjust(5))
    for warrior in warriors:
        print "%s %s %s %s" % (("%s (%s)" % (warrior.name, warrior.author)).ljust(40),
                               str(warrior.wins).rjust(5),
                               str(warrior.ties).rjust(5),
                               str(warrior.losses).rjust(5))

    # keeps display open if paused, until quit
    while paused:
        for event in pygame.event.get():
            if event.type == QUIT:
                paused = False

    # exit pygame
    pygame.quit()

