;Name   Rato Replicante
;Author Rodrigo Setti
;Strat  Mantém um processo ininterrupto de
;Strat  criação de cópias funcionais.

org inicio

vetores dat.f   $0,         $2981       ;vetores de copia
inicio  mov.i   }vetores,   >vetores    ;copia instrução e incrementa vetores
        jmn.b   $inicio,    *vetores    ;loop de cópia -> enquanto nao encontrou um zero em B
        spl.b   <vetores,   {vetores    ;cria processo na cópia (ajuda a reestruturar ponteiro)
        add.x   #-31,       $-4         ;reestrutura ponteiros
        jmz.a   $inicio,    {vetores    ;loop do programa (ajuda a reestruturar ponteiro)
                                        ;ou se suicida se o programa estiver alterado
