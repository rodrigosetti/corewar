;Name	Jumper Clear
;Author	Rodrigo Setti
;Strat	Core-Clear que de tempo em tempo
;Strat	muda de posição.

Nop.b	#0,	#-986

Mov.i	$-2,	$10
Nop.b	>-1,	>-1
Djn.b	$-2,	#493

Mov.ab	#493,	$-1
Mov.ab	#10,	$-4

Mov.i	*-6,	@-6
Nop.b	}-7,	>-7
Sne.ab	$-8,	#11

Jmp.b	$-994,	#0

Jmp.b	$-4,	#0