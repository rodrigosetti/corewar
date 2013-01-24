#! /usr/bin/env python
#! coding: utf-8

import unittest

from corewars.redcode import *

DEFAULT_ENV = {'CORESIZE': 8000}

class TestRedcodeAssembler(unittest.TestCase):

    def test_1(self):

        input = """
                ;name dwarf
                ;author A. K. Dewdney
                ;assert CORESIZE % 4 == 0

                org start
                step equ 2004

                loop    add.ab  #step,  start
                start   mov     2, 2
                        jmp.f   $loop ;go back and start over
                """
        warrior = parse(input.split('\n'), DEFAULT_ENV)

        self.assertEquals(1, warrior.start)
        self.assertEquals('dwarf', warrior.name)
        self.assertEquals('A. K. Dewdney', warrior.author)
        self.assertEquals(3, len(warrior))

        self.assertEquals(Instruction(ADD, M_AB, IMMEDIATE, 2004, DIRECT, 1),
                          warrior.instructions[0])
        self.assertEquals(Instruction(MOV, M_I, DIRECT, 2, DIRECT, 2),
                          warrior.instructions[1])
        self.assertEquals(Instruction(JMP, M_F, DIRECT, -2, DIRECT, 0),
                          warrior.instructions[2])

if __name__ == '__main__':
    unittest.main()

