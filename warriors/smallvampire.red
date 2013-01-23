;Name	Small SPL Vampire
;Author	Rodrigo Setti
;Strat	Vampiro comum e muito pequeno.


ORG	inicio

data	Jmp.b	$-4,		#9	;data

;********** VAMPIRE
inicio	Slt.b	$data,		#9	;overrun protection
	Mov.i	$data,		@data	;copies trap catcher
	Add.x	#pmaker,	$data	;steps
tpnter	Jmp.b	$inicio,	#-5	;loop, trap pointer

;********** TRAP
clear	Mov.i	$3,		<tpnter	;clear		<----
pmaker	Spl.b	#0,		#0	;proc. maker
	Jmp.b	$clear,		#0	;loop
