;Name IMPTTres
;Author Rodrigo Setti
;Strat Se move pela memória linearmente,
;Strat análogo ao IMP.

mov.i   $0,     $3
seq.ab  }-1,    #-2
jmp.b   $-2,    >-2
