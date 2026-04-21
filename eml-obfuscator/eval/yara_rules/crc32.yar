rule CRC32_Poly {
    strings:
        $poly = { 20 83 B8 ED }
    condition:
        $poly
}