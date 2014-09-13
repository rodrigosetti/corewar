
# Core War

[![Build Status](https://travis-ci.org/rodrigosetti/corewar.svg?branch=master)](https://travis-ci.org/rodrigosetti/corewar)

The Canadian mathematician A. K. Dewdney (author of "The Planiverse") first
introduced Core War in a series of Scientific American articles
starting in 1984.

> Core War was inspired by a story I heard some years ago about a mischievous
> programmer at a large corporate research laboratory I shall designate X. The
> programmer wrote an assembly-language program called Creeper that would
> duplicate itself every time it was run. It could also spread from one
> computer to another in the network of the X corporation. The program had no
> function other than to perpetuate itself. Before long there were so many
> copies of Creeper that more useful programs and data were being crowded out.
> The growing infestation was not brought under control until someone thought
> of fighting fire with fire. A second self-duplicating program called Reaper
> was written.  Its purpose was to destroy copies of Creeper until it could
> find no more and then to destroy itself. Reaper did its job, and things were
> soon back to normal at the X lab.

In this game, computer programs (called "Warriors") compete in a virtual arena
for digital supremacy. Warriors are written in an Assembly dialect called
"Redcode".

[Wikipedia article](http://en.wikipedia.org/wiki/Core_War)

This is a Python implementation of the MARS (Memory Array Redcode Simulator).

    usage: graphics.py [-h] [--rounds [ROUNDS]] [--paused] [--size [CORESIZE]]
                       [--cycles [CYCLES]] [--processes [MAXPROCESSES]]
                       [--length [MAXLENGTH]] [--distance [MINDISTANCE]]
                       WARRIOR [WARRIOR ...]

    MARS (Memory Array Redcode Simulator)

    positional arguments:
      WARRIOR               Warrior redcode filename

    optional arguments:
      -h, --help            show this help message and exit
      --rounds [ROUNDS], -r [ROUNDS]
                            Rounds to play
      --paused              Start each round paused
      --size [CORESIZE], -s [CORESIZE]
                            The core size
      --cycles [CYCLES], -c [CYCLES]
                            Cycles until tie
      --processes [MAXPROCESSES], -p [MAXPROCESSES]
                            Max processes
      --length [MAXLENGTH], -l [MAXLENGTH]
                            Max warrior length
      --distance [MINDISTANCE], -d [MINDISTANCE]
                            Minimum warrior distance
