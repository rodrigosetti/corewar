;Name Polen
;Author Rodrigo Setti
;Strat Lança vários "esporos" com processos
;Strat pela memória, difíceis de serem localizados
;Strat e exterminados, porém são inofensivos.

org 2

jmp.f   #0,     <-3

slt.b	$1,	#4
mov.i	$-2,	$973
spl.f   @-1,    }1
add.ab	#971,	$-2
jmp.f   $-4,    #0
