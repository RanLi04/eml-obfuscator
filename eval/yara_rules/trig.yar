rule SinCos_FPU {
    strings:
        $fld = { D9 EB }
        $fsin = { D9 FE }
    condition:
        $fld and $fsin
}