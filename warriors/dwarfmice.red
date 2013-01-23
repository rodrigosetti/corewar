;Name Dwarf Mice
;Author Rodrigo Setti
;Strat Inicia um processo de criação de
;Strat Dwarfs pela memória.

MOV.i	$0,	$-396	;copia instrução
SEQ.i	}-1,	$5	;incrementa e verifica fim da copia
JMP.b	$-2,	>-2	;incrementa e retorna p/ copia

SPL.b	$-399,	#0	;cria processo na copia

spl.b	#2,	}0	;Dwarf avançado.
mov.i	$2,	}-1
dat.f	}-2,	}-2