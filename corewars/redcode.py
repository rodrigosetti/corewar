# coding: utf-8

import re

__all__ = ['parse', 'DAT', 'MOV', 'ADD', 'SUB', 'MUL', 'DIV', 'MOD', 'JMP',
           'JMZ', 'JMN', 'DJN', 'SPL', 'SLT', 'CMP', 'SEQ', 'SNE', 'NOP',
           'LDP', 'STP', 'M_A', 'M_B', 'M_AB', 'M_BA', 'M_F', 'M_X',
           'IMMEDIATE', 'DIRECT', 'INDIRECT_B', 'PREDEC_B', 'POSTINC_B',
           'INDIRECT_A', 'PREDEC_A', 'POSTINC_A', 'Instruction', 'Warrior']

DAT = 0     # terminate process
MOV = 1     # move from A to B
ADD = 2     # add A to B, store result in B
SUB = 3     # subtract A from B, store result in B
MUL = 4     # multiply A by B, store result in B
DIV = 5     # divide B by A, store result in B if A <> 0, else terminate
MOD = 6     # divide B by A, store remainder in B if A <> 0, else terminate
JMP = 7     # transfer execution to A
JMZ = 8     # transfer execution to A if B is zero
JMN = 9     # transfer execution to A if B is non-zero
DJN = 10    # decrement B, if B is non-zero, transfer execution to A
SPL = 11    # split off process to A
SLT = 12    # skip next instruction if A is less than B
CMP = 13    # same as SEQ
SEQ = 14    # Skip next instruction if A is equal to B
SNE = 15    # Skip next instruction if A is not equal to B
NOP = 16    # No operation
LDP = 17    # Load P-space cell A into core address B
STP = 18    # Store A-number into P-space cell B

# Instructions read and write A-fields.
M_A = 0

# Instructions read and write B-fields.
M_B = 1

# Instructions read the A-field of the A-instruction and the B-field of the
# B-instruction and write to B-fields.
M_AB = 2

# Instructions read the B-field of the A-instruction and the A-field of the
# B-instruction and write to A-fields.
M_BA = 3

# Instructions read both A- and B-fields of the A and B-instruction and
# write to both A- and B-fields (A to A and B to B).
M_F = 4

# Instructions read both A- and B-fields of the A and B-instruction  and
# write  to both A- and B-fields exchanging fields (A to B and B to A).
M_X = 5

# Instructions read and write entire instructions.
M_I = 6

IMMEDIATE = 0   # immediate
DIRECT = 1      # direct
INDIRECT_B = 2  # indirect using B-field
PREDEC_B  = 3   # predecrement indirect using B-field
POSTINC_B = 4   # postincrement indirect using B-field
INDIRECT_A = 5  # (*) indirect using A-field
PREDEC_A = 6    # (*) predecrement indirect using A-field
POSTINC_A = 7   # (*) postincrement indirect using A-field

INSTRUCTION_REGEX = re.compile(r'([a-z]{3})'  # opcode
                               r'(?:\s*\.\s*([abfxi]{1,2}))?' # optional modifier
                               r'(?:\s*([#\$\*@\{<\}>])?\s*([^,$]+))?' # optional first value
                               r'(?:\s*,\s*([#\$\*@\{<\}>])?\s*(.+))?$', # optional second value
                               re.I)

OPCODES = {'DAT': DAT, 'MOV': MOV, 'ADD': ADD, 'SUB': SUB, 'MUL': MUL,
           'DIV': DIV, 'MOD': MOD, 'JMP': JMP, 'JMZ': JMZ, 'JMN': JMN,
           'DJN': DJN, 'SPL': SPL, 'SLT': SLT, 'CMP': CMP, 'SEQ': SEQ,
           'SNE': SNE, 'NOP': NOP, 'LDP': LDP, 'STP': STP}

MODIFIERS = {'A': M_A, 'B': M_B, 'AB': M_AB, 'BA': M_BA, 'F': M_F, 'X': M_X,
             'I': M_I}

MODES = { '#': IMMEDIATE, '$': DIRECT, '@': INDIRECT_B, '<': PREDEC_B,
          '>': POSTINC_B, '*': INDIRECT_A, '{': PREDEC_A, '}': PREDEC_B }

# ICWS'88 to ICWS'94 Conversion
# The default modifier for ICWS'88 emulation is determined according to the
# table below.
#        Opcode                             A-mode    B-mode    modifier
DEFAULT_MODIFIERS = {
        ('DAT',)                       : {('#$@<>', '#$@<>'): 'F'},
        ('MOV','CMP')                  : {('#'    , '#$@<>'): 'AB',
                                          ('$@<>' , '#'    ): 'B' ,
                                          ('$@<>' , '$@<>' ): 'I'},
        ('ADD','SUB','MUL','DIV','MOD'): {('#'    , '#$@<>'): 'AB',
                                          ('$@<>' , '#'    ): 'B' ,
                                          ('$@<>' , '$@<>' ): 'F'},
        ('SLT',)                       : {('#'    , '#$@<>'): 'AB',
                                          ('$@<>' , '#$@<>'): 'B'},
        ('JMP','JMZ','JMN','DJN','SPL'): {('#$@<>', '#$@<>'): 'B'}
    }

# Transform the readable form above, into the internal representation
DEFAULT_MODIFIERS = dict((tuple(OPCODES[opcode] for opcode in opcodes),
                         dict(((tuple(MODES[a] for a in ab_modes[0]),
                                tuple(MODES[b] for b in ab_modes[1])),
                               MODIFIERS[modifier]) for ab_modes, modifier in ab_modes_modifiers.iteritems()))
                         for opcodes, ab_modes_modifiers in DEFAULT_MODIFIERS.iteritems())

class Warrior(object):
    "An encapsulation of a Redcode Warrior, with instructions and meta-data"

    def __init__(self, name=None, author=None, date=None, version=None,
                 strategy=None, start=0):
        self.name = name
        self.author = author
        self.date = date
        self.version = version
        self.strategy = strategy
        self.start = start
        self.instructions = []

    def __len__(self):
        return len(self.instructions)

    def __repr__(self):
        return "<Warrior name=%s %d instructions>" % (self.name, len(self.instructions))

class Instruction(object):
    "An encapsulation of a Redcode instruction."

    def __init__(self, opcode, modifier=None, a_mode=None, a_number=0,
                 b_mode=None, b_number=0):
        self.opcode = OPCODES[opcode.upper()]
        self.a_mode = MODES[a_mode if a_mode else '$']
        self.b_mode = MODES[b_mode if b_mode else '$']
        self.a_number = a_number if a_number else 0
        self.b_number = b_number if b_number else 0

        # this should be last, to decide on the default modifier
        self.modifier = MODIFIERS[modifier.upper()] if modifier else self.default_modifier()

    def default_modifier(self):
        for opcodes, modes_modifiers in DEFAULT_MODIFIERS.iteritems():
            if self.opcode in opcodes:
                for ab_modes, modifier in modes_modifiers.iteritems():
                    a_modes, b_modes = ab_modes
                    if self.a_mode in a_modes and self.b_mode in b_modes:
                        return modifier
        raise RuntimeError("Error getting default modifier")

    def __repr__(self):
        # inverse lookup the instruction values
        opcode   = next(key for key,value in OPCODES.iteritems() if value==self.opcode)
        modifier = next(key for key,value in MODIFIERS.iteritems() if value==self.modifier)
        a_mode   = next(key for key,value in MODES.iteritems() if value==self.a_mode)
        b_mode   = next(key for key,value in MODES.iteritems() if value==self.b_mode)

        return "<%s.%s %s%d, %s%d>" % (opcode, modifier, a_mode, self.a_number,
                                      b_mode, self.b_number)

def parse(input, environment={}):
    """ Parse a Redcode code from a line iterator (input) returning a Warrior
        object."""

    found_recode_info_comment = False
    lines = []
    labels = {}
    code_address = 0

    warrior = Warrior()
    warrior.strategy = []

    # first pass
    for n, line in enumerate(input):
        line = line.strip()
        if line:
            # process info comments
            m = re.match(r'^;redcode\w*$', line, re.I)
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

            m = re.match(r'^;date\s+(.+)$', line, re.I)
            if m:
                warrior.date = m.group(1).strip()
                continue

            m = re.match(r'^;version\s+(.+)$', line, re.I)
            if m:
                warrior.version = m.group(1).strip()
                continue

            m = re.match(r'^;strat(?:egy)?\s+(.+)$', line, re.I)
            if m:
                warrior.strategy.append(m.group(1).strip())
                continue

            # Test if assert expression evaluates to true
            m = re.match(r'^;assert\s+(.+)$', line, re.I)
            if m:
                if not eval(m.group(1), environment):
                    raise AssertionError("Assertion failed: %s, line %d" % (line, n))
                continue

            # ignore other comments
            m = re.match(r'^([^;]*)\s*;', line)
            if m:
                # rip off comment from the line
                line = m.group(1).strip()
                # if this is a comment line
                if not line: continue

            # Match ORG
            m = re.match(r'ORG\s+(.+)\s*$', line, re.I)
            if m:
                warrior.start = m.group(1)
                continue

            # Match END
            m = re.match(r'END(?:\s+([^\s].+))?$', line, re.I)
            if m:
                if m.group(1):
                    warrior.start = m.group(1)
                break # stop processing (end of redcode)

            # Keep matching the first word until it's no label anymore
            while True:
                m = re.match(r'([a-z]\w*)\s*(.+)\s*$', line)
                if m:
                    label_candidate = m.group(1)
                    if label_candidate.upper() not in OPCODES.keys():
                        labels[label_candidate] = code_address

                        # strip label off and keep looking
                        line = m.group(2)
                        continue
                        break
                # its an instruction, not label. proceed OR no match, probably
                # a all-value-omitted instruction.
                break

            # At last, it should match an instruction
            m = INSTRUCTION_REGEX.match(line)
            if not m:
                raise ValueError('Error at line %d: expected instruction in expression: "%s"' %
                                 (n, line))
            else:
                opcode, modifier, a_mode, a_number, b_mode, b_number = m.groups()

                if opcode.upper() not in OPCODES:
                    raise ValueError('Invalid opcode: %s in line %d: "%s"' %
                                     (opcode, n, line))
                if modifier is not None and modifier.upper() not in MODIFIERS:
                    raise ValueError('Invalid modifier: %s in line %d: "%s"' %
                                     (modifier, n, line))

                # add parts of instruction read. the fields should be parsed
                # as an expression in the second pass, to expand labels
                warrior.instructions.append(Instruction(opcode, modifier,
                                                        a_mode, a_number,
                                                        b_mode, b_number))

            # increment code counting
            code_address += 1


    # join strategy lines with line breaks
    warrior.strategy = '\n'.join(warrior.strategy)

    # evaluate start expression
    if isinstance(warrior.start, str):
        warrior.start = eval(warrior.start, environment, labels)

    # second pass
    for n, instruction in enumerate(warrior.instructions):

        # create a dictionary of relative labels addresses to be used as a local
        # eval environment
        relative_labels = dict((name, address-n) for name, address in labels.iteritems())

        # evaluate instruction fields using global environment and labels
        if isinstance(instruction.a_number, str):
            instruction.a_number = eval(instruction.a_number, environment, relative_labels)
        if isinstance(instruction.b_number, str):
            instruction.b_number = eval(instruction.b_number, environment, relative_labels)

    return warrior

