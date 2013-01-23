;Name   Core Clear
;Author Rodrigo Setti
;Strat realiza uma "limpeza" da memória.
;Strat contém recurso de auto-proteção.

org	0

slt.ab	#3,	#3	;verifica se ponteiro esta sobre si mesmo
mov.i	$2,	}-1	;se nao, copia instr. vazia e incrementa pont.
jmp.b	$-2,	}-2	;loop e incrementa ponteiro

dat.f	#130,	#672