;Name Dwarf Jumper
;Author	Rodrigo Setti
;Strat Lança códigos de "prisão" pela memória
;Strat que mantém os processos inimigos
;Strat paralizados, porém, não é mortal.


org 1

mov.i	$1,	>2
jmp.f   $-1,    >1
