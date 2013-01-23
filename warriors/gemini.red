;name Gemini
;author A. K. Dewdney

        DAT.f    $0,    $0
        DAT.f    $0,     $99
        MOV.i   @-2,    @-1
        SNE.b   $-3,     #9
        JMP.f   $4,     $0
        ADD.ab  #1,     $-5
        ADD.ab  #1,     $-5
        JMP.f   $-5,    $0
        MOV.ab  #99,    $93
        JMP.f   $93,    $0

        END     2
