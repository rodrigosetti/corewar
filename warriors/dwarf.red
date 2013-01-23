;name dwarf
;author A. K. Dewdney

org inicio

adic	add.ab  #2004,	$inicio
inicio	mov.i   $2,	$2
	jmp.f   $adic,	#0
