# coding: utf-8

import re

INSTRUCTION_REGEX = re.compile(r'([a-z]{3})'  # opcode
                               r'(?:\s*\.\s*([abfxi]{1,2}))?' # optional modifier
                               r'(?:\s+([#\$\*@\{<\}>])?\s*([^,]+),)?' # optional first op (must have second)
                               r'(?:\s+([#\$\*@\{<\}>])?\s*(.+))?$', # optional second or only operand
                               re.I)

OPCODES = [
    'DAT',     # terminate process
    'MOV',     # move from A to B
    'ADD',     # add A to B, store result in B
    'SUB',     # subtract A from B, store result in B
    'MUL',     # multiply A by B, store result in B
    'DIV',     # divide B by A, store result in B if A <> 0, else terminate
    'MOD',     # divide B by A, store remainder in B if A <> 0, else terminate
    'JMP',     # transfer execution to A
    'JMZ',     # transfer execution to A if B is zero
    'JMN',     # transfer execution to A if B is non-zero
    'DJN',     # decrement B, if B is non-zero, transfer execution to A
    'SPL',     # split off process to A
    'SLT',     # skip next instruction if A is less than B
    'CMP',     # same as SEQ
    'SEQ',     # (*) Skip next instruction if A is equal to B
    'SNE',     # (*) Skip next instruction if A is not equal to B
    'NOP',     # (*) No operation
    'LDP',     # (+) Load P-space cell A into core address B
    'STP',     # (+) Store A-number into P-space cell B
    ]

MODIFIERS = [
    'A',  # Instructions read and write A-fields.

    'B',  # Instructions read and write B-fields.

    'AB', # Instructions read the A-field of the A-instruction  and
          # the B-field of the B-instruction and write to B-fields.

    'BA', # Instructions read the B-field of the A-instruction  and
          # the A-field of the B-instruction and write to A-fields.

    'F',  # Instructions read both A- and B-fields of  the  the  A and
          # B-instruction and write to both A- and B-fields (A to A and B
          # to B).

    'X',  # Instructions read both A- and B-fields of  the  the  A and
          # B-instruction  and  write  to both A- and B-fields exchanging
          # fields (A to B and B to A).

    'I',  # Instructions read and write entire instructions.
    ]

class Warrior(object):

    def __init__(self, name=None, author=None, strategy=None):
        self.name = name
        self.author = author
        self.strategy = strategy
        self.instructions = []

    def __repr__(self):
        return "<Warrior name=%s %d instructions>" % (self.name, len(self.instructions))

class Instruction(object):

    def __init__(self, opcode, modifier=None, addr_mode_a=None, field_a=0,
                 addr_mode_b=None, field_b=0):
        self.opcode = opcode.upper()
        self.modifier = modifier.upper() if modifier else ''
        self.addr_mode_a = addr_mode_a if addr_mode_a else ''
        self.field_a = field_a if field_a else 0
        self.addr_mode_b = addr_mode_b if addr_mode_b else ''
        self.field_b = field_b if field_b else 0

    def __repr__(self):
        return "<%s%s %s%d, %s%d>" % (self.opcode,
                                      '.' + self.modifier if self.modifier else '',
                                      self.addr_mode_a, self.field_a,
                                      self.addr_mode_b, self.field_b)

def parse(input, environment={}):

    found_recode_info_comment = False
    lines = []
    labels = {}
    code_address = 0
    start_expr = '0'

    warrior = Warrior()

    # first pass
    for n, line in enumerate(input):
        line = line.strip()
        if line:
            # process info comments
            m = re.match(r'^;redcode(?:-94)?$', line, re.I)
            if m:
                if found_recode_info_comment:
                    # stop reading, found second ;redcode
                    break;
                else:
                    # first ;redcode ignore all input before
                    lines = []
                    found_recode_info_comment = True
                continue

            m = re.match(r'^;name\s+(.+)$', line, re.I)
            if m:
                warrior.name = m.group(1).strip()
                continue

            m = re.match(r'^;author\s+(.+)$', line, re.I)
            if m:
                warrior.author = m.group(1).strip()
                continue

            # Test if assert expression evaluates to true
            m = re.match(r'^;assert\s+(.+)$', line, re.I)
            if m:
                if not eval(m.group(1), environment):
                    raise AssertionError("Assertion failed: %s, line %d" % (line, n))
                continue

            # ignore other comments
            if line.startswith(';'):
                continue

            # Match ORG
            m = re.match(r'ORG\s+(.+)\s*$', line, re.I)
            if m:
                start_expr = m.group(1)
                continue

            # Match END
            m = re.match(r'END(?:\s+([^\s].+))?$', line, re.I)
            if m:
                if m.group(1):
                    start_expr = m.group(1)
                break # stop processing (end of redcode)

            # Match label
            m = re.match(r'(\w+)\s*:\s*(.*)\s*$', line)
            if m:
                labels[m.group(1)] = code_address

                # strip label off and continue parsing
                line = m.group(2)

            # At last, it should match an instruction
            m = INSTRUCTION_REGEX.match(line)
            if not m:
                raise ValueError('Error at line %d: expected instruction in expression: "%s"' %
                                 (n, line))
            else:
                opcode, modifier, addr_mode_a, field_a, addr_mode_b, field_b = m.groups()

                if opcode.upper() not in OPCODES:
                    raise ValueError('Invalid opcode: %s in line %d: "%s"' %
                                     (opcode, n, line))
                if modifier is not None and modifier.upper() not in MODIFIERS:
                    raise ValueError('Invalid modifier: %s in line %d: "%s"' %
                                     (modifier, n, line))

                # add parts of instruction read. the fields should be parsed
                # as an expression in the second pass, to expand labels
                warrior.instructions.append(Instruction(opcode, modifier,
                                                        addr_mode_a, field_a,
                                                        addr_mode_b, field_b))

            # increment code counting
            code_address += 1


    # second pass
    for n, instruction in enumerate(warrior.instructions):

        # create a dictionary of relative labels addresses to be used as a local
        # eval environment
        relative_labels = dict((name, address-n) for name, address in labels.iteritems())

        # evaluate instruction fields using global environment and labels
        if isinstance(instruction.field_a, str):
            instruction.field_a = eval(instruction.field_a, environment, relative_labels)
        if isinstance(instruction.field_b, str):
            instruction.field_b = eval(instruction.field_b, environment, relative_labels)

    return warrior

