;Name	Dwarf Vampire
;Author	Rodrigo Setti
;Strat	Vampiro, lança códigos de captura pela
;Strat	memória e transferem processos inimigos
;Strat	para a armadilha - que é um dwarf mal
;Strat	ajustado para atingir a si mesmo quando
;Strat	necessário, matando os prisioneiros.

org	inicio

armad	mov.i	$bomba,		$-2	;Armadilha(Dwarf desajustado)
	sub.ab	#4,		$armad	
	jmp.b   $armad,		$0      ;instr. de altera entre DAT e JMP

bomba	dat.f	$0,		$0	;"bomba" da armadilha
incr	dat.f	$-4,		$4	;incrementos p/ capturador
capt	jmp.b   $-10,		$5	;capturador

	dat.f	$0,		$0	;JMP	$-6

inicio	mov.i	$capt,		@capt	;escreve capturador no core
	add.f	$incr,		$capt	;incrementa ponteiros do capturador
	jmp.b   $inicio,    	#0      ;reincia loop
