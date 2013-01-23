;Name	Scanner Vampire
;Author	Rodrigo Setti
;Strat	Procura por campos A e B
;Strat	diferentes de 0 e lança
;Strat	JMPs de captura.


ORG	3

;*** TRAP ***

Spl.b	#0,	#0	;proc maker(scan pointer)
Mov.i	$-2,	>9	;clear
Jmp.b	$-2,	#0	;loop

;*** VAMPIRE ***

Jmz.f	#0,	{-3	;scaner

Slt.a  	#11,	$-4	;overun protection
Jmp.b	$-2,	{-5	;return to scaner

Mov.a	$-6,	$4	;addressing formula
Mul.a	#-1,	$3	;...
Mov.i	$2,	*-8	;copies trap capturer

Jmp.b	$-6,	{-9	;loop

Jmp.b	$0,	#1	;trap capturer data (trap pointer)




