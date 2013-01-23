;Name	ImpThru
;Author	Rodrigo Setti
;Strat Deixa o IMP passar livremente.

org 2

mov.i	$3,	$4
jmp.b	$-1,	>-1

jmp.b	$0,	<-3

