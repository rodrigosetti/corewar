;Name Dwarf Avançado
;Author Rodrigo Setti
;Strat Dwarf muito mais avançado que o
;Strat clássico, utiliza um "SPL 0" e
;Strat incrementa seu ponteiro utilizando
;Strat pos-incressores.


spl.b	#2,	}0	;alimentador de processos e incrementa pont.
mov.i	$2,	}-1	;copia instr. vazia e incrementa ponteiro
dat.f	}-2,	}-2	;elimina processo e incrementa ponteiro(2x)

