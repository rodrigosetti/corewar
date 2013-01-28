;redcode
;name Validate 1.1R
;author Stefan Strack
;strategy System validation program - based on Mark Durham's validation suite
;
;   This program tests your corewar system for compliance with the ICWS88-
;   standard and compatibility with KotH. It self-ties (i.e. loops forever)
;   if the running system is ICWS88-compliant and uses in-register evaluation;
;   suicides (terminates) if the interpreter is not ICWS compliant and/or uses
;   in-memory evaluation. A counter at label 'flag' can be used to determine
;   where the exception occurred.
;
;   Tests:
;   -all opcodes and addressing modes
;   -ICWS88-style ADD/SUB
;   -ICWS88-style SPL
;   -correct timing
;   -in-memory vs. in-register evaluation
;   -core initialization
;
;   Version 1.1: added autodestruct in case process gets stuck


;assert MAXLENGTH >= 90

start   spl l1,count+1
        jmz <start,0
count   djn count,#36      ;time cycles
        sub #1,@start
clear   mov t1,<last+2     ;autodestruct if stuck
        jmp clear
t1      dat #0,#1
t2      dat #0,#3
l1      spl l2
        dat <t2,<t2
l2      cmp t1,t2
        jmp fail
        spl l4
        jmz l3,<0
t3      dat #0,#1
t4      dat #0,#2
l3      jmp @0,<0
l4      jmp <t5,#0
        jmp l5
t5      dat #0,#0
t6      dat #0,#-1
l5      cmp t3,t4
        jmp fail
        cmp t5,t6
        jmp fail
        jmp <t7,<t7
        jmp l6
t7      dat #0,#0
t8      dat #0,#-2
l6      cmp t7,t8
        jmp fail
        mov t9,<t9         ;test in-memory evaluation
t9      jmn l7,1
t10     jmn l7+1,1
l7      cmp t9,t10
        jmp fail
        mov @0,<t11
t11     jmn l8,1
t12     jmn l8+1,1
l8      cmp t11,t12
        jmp fail
        spl l9
        mov <t13,t14
t13     dat <0,#1
t14     dat <0,#1
t15     dat <0,#-1
l9      mov <t16,t16
t16     jmz l10,1
        jmp fail
l10     cmp t13,t15
        jmp fail
        add t17,<t17
t17     jmp 1,1
t18     jmp 2,1
        cmp t17,t18
        jmp fail
        add @0,<t19
t19     jmp 1,1
        jmp fail
        cmp t18,t19
        jmp fail
        spl l11            ;ICWS86 SPL will fail here
        cmp t20,t21
        jmp l12
        jmp fail
l11     sub <t20,t20
t20     dat #2,#1
t21     dat #0,#0
l12     cmp t20,t21
        jmp fail
t22     sub <t23,<t23
t23     jmp l13,1
t24     sub <-2,<1
t25     jmp l13+2,-1
l13     cmp t22,t24
        jmp fail
        cmp t23,t25
        jmp fail
        cmp start-1,t26    ;Core initialization dat 0,0
        jmp l14
        jmp fail
t26     dat #0,#0
l14     slt #0,count       ;check cycle timer
        jmp success
fail    mov count,flag     ;save counter for post-mortem debugging
        mov t1,count       ;kill counter
        jmp clear          ;and auto-destruct
flag    dat #0, #0
success mov flag,clear     ;cancel autodestruct
last    jmp 0              ;and loop forever

        end start
