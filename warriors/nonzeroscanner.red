;Name	Non-Zero Scanner
;Author	Rodrigo Setti
;Strat	Procura por campos-A e B diferentes
;Strat	de zero e bombardeia.

jmz.f	#0,	{0	;decrementa e testa se campos A e B= 0

slt.ab	$-1,	#4	;verifica se campos nao sao dele proprio
mov.i	$2,	*-2	;copia instr. vazia sobre instr.
jmp.b	$-3,	#0	;retorna para testador