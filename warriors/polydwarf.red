;Name PolyDwarfs
;Author Rodrigo Setti
;Strat Cria 11 Dwarfs em posições estratégicas.

org 4

add.a   #800,   $7	;muda pos. dos ponteiros
add.ab  #800,   $5
add.ab  #800,   $3
add.ab  #800,   $1

mov.i   $5,     $809	;copia dwarf
mov.i   $5,     $809
mov.i   $5,     $809
spl.f   $806,   #0	;cria processo no dwarf
djn.b   $-8,    #10	;retorna para copia se ainda nao terminou

spl.b	#2,	}0	;Dwarf avançado.
mov.i	$2,	}-1
dat.f	}-2,	}-2
