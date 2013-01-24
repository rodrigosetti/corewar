#! /usr/bin/env python
#! coding: utf-8

import unittest

from corewar import redcode, mars

DEFAULT_ENV = {'CORESIZE': 8000}

class TestMars(unittest.TestCase):

    def test_dwarf_versus_sitting_duck(self):

        dwarf_code = """
            ;name dwarf
            ;author A. K. Dewdney

            org start

            loop    add.ab  #2004, start
            start   mov     2,     2
                    jmp     loop
        """
        sitting_duck_code = """
            nop
            nop
            nop
            nop
            nop
        """

        dwarf        = redcode.parse(dwarf_code.split('\n'), DEFAULT_ENV)
        sitting_duck = redcode.parse(sitting_duck_code.split('\n'), DEFAULT_ENV)

        simulation = mars.MARS(warriors=[dwarf, sitting_duck])

        # run simulation for at most
        for x in xrange(8000):
            simulation.step()
            if not dwarf.task_queue or not sitting_duck.task_queue:
                break
        else:
            self.fail("Running for too long and both warriors still alive")

        self.assertEquals(1, len(dwarf.task_queue))
        self.assertEquals(0, len(sitting_duck.task_queue))


