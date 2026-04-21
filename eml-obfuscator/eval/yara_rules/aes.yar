rule AES_Ttables {
    strings:
        $te0 = { C6 63 63 A5 }
        $te1 = { F7 7C 7C 84 }
    condition:
        any of them
}