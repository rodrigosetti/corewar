;Name Parasita
;Author	Rodrigo Setti
;Strat Localiza programa inimigo e lança
;Strat um processo "parasita" com o objetivo
;Strat de se aproveitar da estratégia do
;Strat oponente para vencer.

org     4

Nop.b   #99,    #99
Nop.b   #99,    #99
Nop.b   #99,    #99
Dat.f   $0,     $0

Seq.i   $-1,    @2
Spl.b   @1,     #0

Seq.i   $-3,    $100
Add.ab  #100,   $-1

Add.ab	#3,	$-2
Jmp.b   $-5,    #0

