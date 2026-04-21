#include <stdint.h>

// Simplified AES S-box (first 16 bytes for demonstration)
static const uint8_t sbox[256] = {
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    // ... remaining entries omitted for brevity; full S-box can be added
};

uint8_t sub_byte(uint8_t x) {
    return sbox[x];
}

uint32_t crc32_byte(uint32_t crc, uint8_t byte) {
    // Simplified CRC32 inner loop
    crc ^= byte;
    for (int i = 0; i < 8; i++) {
        crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
    }
    return crc;
}