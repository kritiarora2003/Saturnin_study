#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "crypto_aead.h"

void saturnin_block_encrypt(int R, int D, const uint8_t *key, uint8_t *buf);
void saturnin_block_decrypt(int R, int D, const uint8_t *key, uint8_t *buf);

#define SATURNIN_SHORT_R 1
#define SATURNIN_SHORT_D 6

unsigned long long PLAINTEXT_LEN = 15;
uint8_t PLAINTEXT[15] = {
    0x03,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,
    0x00,0x00,0x00
};

uint8_t NONCE[16] = {
    0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00
};

uint8_t KEY[32] = {
    0x00,0x01,0x02,0x03,
    0x04,0x05,0x06,0x07,
    0x08,0x09,0x0a,0x0b,
    0x0c,0x0d,0x0e,0x0f,
    0x10,0x11,0x12,0x13,
    0x14,0x15,0x16,0x17,
    0x18,0x19,0x1a,0x1b,
    0x1c,0x1d,0x1e,0x1f
};

// AEAD encrypt/decrypt functions
int crypto_aead_encrypt(unsigned char *c, unsigned long long *clen,
    const unsigned char *m, unsigned long long mlen,
    const unsigned char *ad, unsigned long long adlen,
    const unsigned char *nsec,
    const unsigned char *npub,
    const unsigned char *k)
{
    uint8_t tmp[32];
    (void)ad; (void)nsec;

    if(adlen != 0) return -2;
    if(mlen > 15) return -2;

    memcpy(tmp, npub, 16);
    if(mlen > 0) memcpy(tmp + 16, m, mlen);
    tmp[16 + mlen] = 0x80;
    memset(tmp + 16 + mlen + 1, 0x00, 15 - mlen);

    saturnin_block_encrypt(SATURNIN_SHORT_R, SATURNIN_SHORT_D, k, tmp);
    memcpy(c, tmp, 32);
    *clen = 32;
    return 0;
}

int crypto_aead_decrypt(unsigned char *m, unsigned long long *mlen,
    unsigned char *nsec,
    const unsigned char *c, unsigned long long clen,
    const unsigned char *ad, unsigned long long adlen,
    const unsigned char *npub,
    const unsigned char *k)
{
    uint8_t tmp[32];
    unsigned tcc, notfound, u;
    int i;

    (void)ad; (void)nsec;
    if(adlen != 0) return -2;
    if(clen != 32) return -1;

    memcpy(tmp, c, 32);
    saturnin_block_decrypt(SATURNIN_SHORT_R, SATURNIN_SHORT_D, k, tmp);

    tcc = 0;
    for(i=0;i<16;i++) tcc |= tmp[i] ^ npub[i];

    notfound = 0xFF; u = 0;
    for(i=15;i>=0;i--){
        unsigned b = tmp[16+i];
        unsigned f = notfound & -(1 - (((b ^ 0x80) + 0xFF) >> 8));
        u |= f & (unsigned)i;
        notfound &= ~f;
        tcc |= notfound & ((b + 0xFF) >> 8);
    }
    tcc |= notfound;

    if(tcc != 0) return -1;

    memcpy(m, tmp+16, u);
    *mlen = u;
    return 0;
}

int main() {
    uint8_t ciphertext[32];
    unsigned long long clen;

    // Encrypt
    if(crypto_aead_encrypt(ciphertext, &clen, PLAINTEXT, PLAINTEXT_LEN, NULL, 0, NULL, NONCE, KEY) != 0){
        printf("Encryption failed\n");
        return 1;
    }

    printf("Ciphertext (%llu bytes): ", clen);
    for(int i=0;i<clen;i++) printf("%02x", ciphertext[i]);
    printf("\n");

    // // Decrypt to verify
    // uint8_t decrypted[16];
    // unsigned long long decrypted_len;
    // if(crypto_aead_decrypt(decrypted, &decrypted_len, NULL, ciphertext, clen, NULL, 0, NONCE, KEY) != 0){
    //     printf("Decryption failed\n");
    //     return 1;
    // }

    // printf("Decrypted plaintext: ");
    // for(int i=0;i<decrypted_len;i++) printf("%02x", decrypted[i]);
    // printf("\n");

    // printf("Ciphertext (%llu bytes): ", clen);
    // for(int i=0;i<clen;i++) printf("%02x", ciphertext[i]);
    // printf("\n");

    return 0;
}
