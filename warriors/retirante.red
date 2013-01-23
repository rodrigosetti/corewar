;Name Retirante
;Author	Rodrigo Setti
;Strat Mantém um processo de mudança constante
;Strat de endereço na memória, o que o torna
;Strat difícil de ser localizado.

mov.i   $0,     $1002	;copia instrução
jmz.b	>-1,	}-1	;verifica fim e incrementa copia
jmp.b	$-2,	#0	;pula para copia
