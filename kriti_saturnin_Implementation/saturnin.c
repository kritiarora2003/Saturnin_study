/* ======================================================================== */
/*
 * Saturnin block cipher implementation (reference code, not optimized).
 */

#include <string.h>
#include <stdint.h>
#include <stdio.h>

// print state to see it in between functions 
// for debugging and educational purposes
static void print_state(uint16_t *state, const char *label, int round, const char *phase) {
    printf("%s - Round %2d [%s]:\n", label, round, phase);
    for (int i = 0; i < 16; i++) {
        printf("%04x ", state[i]);
        if ((i + 1) % 4 == 0)
            printf("\n");
    }
    printf("\n");
}

/*
 * Compute round constants for R super-rounds and domain D.
 * Assumptions:
 *   0 <= R <= 31
 *   0 <= D <= 15
 */
// r is number of rounds
// d is the cipher mode = 6 for saturnin short
static void
make_round_constants(int R, int D, uint16_t *RC0, uint16_t *RC1)
{
	//  r is 10 and d is 6 for saturnin short

	// x0 and x1 is the seed
	// so x0 and x1 are 16 bit long seed taken from a fixed prefix
	uint16_t x0, x1;

	// iterator
	int n;
	// 0xFE00 is a seed initiator
	x0 = x1 = D + (R << 4) + 0xFE00;

	// we do this 16 times
	// we do x0>>15 where we pick the MSB
	// then we check if the MSB was 0 then anything xor 0 is 0
	// else if the MSB was 1 then -1 is ffff so after anding with 2D 
	// we get the taps
	// x<<1 is that MSB is discarded
	// a 0 enters the LSB
	// we run the LFSR 16 times to make
	for (n = 0; n < R; n ++) {
		int i;
		for (i = 0; i < 16; i ++) {
			x0 = (x0 << 1) ^ (0x2D & -(x0 >> 15));
			x1 = (x1 << 1) ^ (0x53 & -(x1 >> 15));
		}
		RC0[n] = x0;
		RC1[n] = x1;
	}
}

/*
 * Apply the S-boxes on the state (sigma_0 and sigma_1).
 */
// i'll have to do it by hand once while having the paper open to see
// exactly how implementing sigma0 and sigma1 at the same time
// on the first 8 blocks is finally outputing as 
// sigma0 on even and sigma1 on odd
static void
S_box(uint16_t *state)
{
	int i;

	for (i = 0; i < 16; i += 8) {
		uint16_t a, b, c, d;

		/* sigma_0 */
		a = state[i + 0];
		b = state[i + 1];
		c = state[i + 2];
		d = state[i + 3];
		a ^= b & c;
		b ^= a | d;
		d ^= b | c;
		c ^= b & d;
		b ^= a | c;
		a ^= b | d;
		state[i + 0] = b;
		state[i + 1] = c;
		state[i + 2] = d;
		state[i + 3] = a;

		/* sigma_1 */
		a = state[i + 4];
		b = state[i + 5];
		c = state[i + 6];
		d = state[i + 7];
		a ^= b & c;
		b ^= a | d;
		d ^= b | c;
		c ^= b & d;
		b ^= a | c;
		a ^= b | d;
		state[i + 4] = d;
		state[i + 5] = b;
		state[i + 6] = a;
		state[i + 7] = c;
	}
}

/*
 * Apply the inverse S-boxes on the state (inv_sigma_0 and inv_sigma_1).
 */
static void
S_box_inv(uint16_t *state)
{
	int i;

	for (i = 0; i < 16; i += 8) {
		uint16_t a, b, c, d;

		/* inv_sigma_0 */
		b = state[i + 0];
		c = state[i + 1];
		d = state[i + 2];
		a = state[i + 3];
		a ^= b | d;
		b ^= a | c;
		c ^= b & d;
		d ^= b | c;
		b ^= a | d;
		a ^= b & c;
		state[i + 0] = a;
		state[i + 1] = b;
		state[i + 2] = c;
		state[i + 3] = d;

		/* inv_sigma_1 */
		d = state[i + 4];
		b = state[i + 5];
		a = state[i + 6];
		c = state[i + 7];
		a ^= b | d;
		b ^= a | c;
		c ^= b & d;
		d ^= b | c;
		b ^= a | d;
		a ^= b & c;
		state[i + 4] = a;
		state[i + 5] = b;
		state[i + 6] = c;
		state[i + 7] = d;
	}
}

/*
 * Apply the linear transform (MDS) on the state.
 */
// mds = maximum distance separable
// this is the matrix multiplication mix cols
// converted into xors for optimization
// like the one we did in aes
static void
MDS(uint16_t *state)
{
	uint16_t x0, x1, x2, x3, x4, x5, x6, x7;
	uint16_t x8, x9, xa, xb, xc, xd, xe, xf;

	x0 = state[0x0];
	x1 = state[0x1];
	x2 = state[0x2];
	x3 = state[0x3];
	x4 = state[0x4];
	x5 = state[0x5];
	x6 = state[0x6];
	x7 = state[0x7];
	x8 = state[0x8];
	x9 = state[0x9];
	xa = state[0xa];
	xb = state[0xb];
	xc = state[0xc];
	xd = state[0xd];
	xe = state[0xe];
	xf = state[0xf];

// here is rotation happening
// t0 is going to temp 
// all others are being rotated
// then at the end we xor the first 2 t0's, temp(old t0) and t1(new t0)
// page 12, first figure
#define MUL(t0, t1, t2, t3)   do { \
		uint16_t mul_tmp = (t0); \
		(t0) = (t1); \
		(t1) = (t2); \
		(t2) = (t3); \
		(t3) = mul_tmp ^ (t0); \
	} while (0)

	x8 ^= xc; x9 ^= xd; xa ^= xe; xb ^= xf; /* C ^= D */
	x0 ^= x4; x1 ^= x5; x2 ^= x6; x3 ^= x7; /* A ^= B */
	MUL(x4, x5, x6, x7);                    /* B = MUL(B) */
	MUL(xc, xd, xe, xf);                    /* D = MUL(D) */
	x4 ^= x8; x5 ^= x9; x6 ^= xa; x7 ^= xb; /* B ^= C */
	xc ^= x0; xd ^= x1; xe ^= x2; xf ^= x3; /* D ^= A */
	MUL(x0, x1, x2, x3);                    /* A = MUL(A) */
	MUL(x0, x1, x2, x3);                    /* A = MUL(A) again */
	MUL(x8, x9, xa, xb);                    /* C = MUL(C) */
	MUL(x8, x9, xa, xb);                    /* C = MUL(C) again */
	x8 ^= xc; x9 ^= xd; xa ^= xe; xb ^= xf; /* C ^= D */
	x0 ^= x4; x1 ^= x5; x2 ^= x6; x3 ^= x7; /* A ^= B */
	x4 ^= x8; x5 ^= x9; x6 ^= xa; x7 ^= xb; /* B ^= C */
	xc ^= x0; xd ^= x1; xe ^= x2; xf ^= x3; /* D ^= A */

#undef MUL

	state[0x0] = x0;
	state[0x1] = x1;
	state[0x2] = x2;
	state[0x3] = x3;
	state[0x4] = x4;
	state[0x5] = x5;
	state[0x6] = x6;
	state[0x7] = x7;
	state[0x8] = x8;
	state[0x9] = x9;
	state[0xa] = xa;
	state[0xb] = xb;
	state[0xc] = xc;
	state[0xd] = xd;
	state[0xe] = xe;
	state[0xf] = xf;
}

/*
 * Apply the inverse of the linear transform (MDS) on the state.
 */
static void
MDS_inv(uint16_t *state)
{
	uint16_t x0, x1, x2, x3, x4, x5, x6, x7;
	uint16_t x8, x9, xa, xb, xc, xd, xe, xf;

	x0 = state[0x0];
	x1 = state[0x1];
	x2 = state[0x2];
	x3 = state[0x3];
	x4 = state[0x4];
	x5 = state[0x5];
	x6 = state[0x6];
	x7 = state[0x7];
	x8 = state[0x8];
	x9 = state[0x9];
	xa = state[0xa];
	xb = state[0xb];
	xc = state[0xc];
	xd = state[0xd];
	xe = state[0xe];
	xf = state[0xf];

#define MULinv(t0, t1, t2, t3)   do { \
		uint16_t mul_tmp = (t3); \
		(t3) = (t2); \
		(t2) = (t1); \
		(t1) = (t0); \
		(t0) = mul_tmp ^ (t1); \
	} while (0)

	x4 ^= x8; x5 ^= x9; x6 ^= xa; x7 ^= xb; /* B ^= C */
	xc ^= x0; xd ^= x1; xe ^= x2; xf ^= x3; /* D ^= A */
	x8 ^= xc; x9 ^= xd; xa ^= xe; xb ^= xf; /* C ^= D */
	x0 ^= x4; x1 ^= x5; x2 ^= x6; x3 ^= x7; /* A ^= B */
	MULinv(x0, x1, x2, x3);                 /* A = MULinv(A) */
	MULinv(x0, x1, x2, x3);                 /* A = MULinv(A) */
	MULinv(x8, x9, xa, xb);                 /* C = MULinv(C) */
	MULinv(x8, x9, xa, xb);                 /* C = MULinv(C) */
	x4 ^= x8; x5 ^= x9; x6 ^= xa; x7 ^= xb; /* B ^= C */
	xc ^= x0; xd ^= x1; xe ^= x2; xf ^= x3; /* D ^= A */
	MULinv(x4, x5, x6, x7);                 /* B = MULinv(B) */
	MULinv(xc, xd, xe, xf);                 /* D = MULinv(D) */
	x8 ^= xc; x9 ^= xd; xa ^= xe; xb ^= xf; /* C ^= D */
	x0 ^= x4; x1 ^= x5; x2 ^= x6; x3 ^= x7; /* A ^= B */

#undef MULinv

	state[0x0] = x0;
	state[0x1] = x1;
	state[0x2] = x2;
	state[0x3] = x3;
	state[0x4] = x4;
	state[0x5] = x5;
	state[0x6] = x6;
	state[0x7] = x7;
	state[0x8] = x8;
	state[0x9] = x9;
	state[0xa] = xa;
	state[0xb] = xb;
	state[0xc] = xc;
	state[0xd] = xd;
	state[0xe] = xe;
	state[0xf] = xf;
}

/*
 * Apply the SR_slice permutation.
 */
static void
SR_slice(uint16_t *state)
{
	int i;

	for (i = 0; i < 4; i ++) {
		state[ 4 + i] = ((state[ 4 + i] & 0x7777) << 1)
			| ((state[ 4 + i] & 0x8888) >> 3);
		state[ 8 + i] = ((state[ 8 + i] & 0x3333) << 2)
			| ((state[ 8 + i] & 0xcccc) >> 2);
		state[12 + i] = ((state[12 + i] & 0x1111) << 3)
			| ((state[12 + i] & 0xeeee) >> 1);
	}
}

/*
 * Apply the inverse of the SR_slice permutation.
 */
static void
SR_slice_inv(uint16_t *state)
{
	int i;

	for (i = 0; i < 4; i ++) {
		state[ 4 + i] = ((state[ 4 + i] & 0x1111) << 3)
			| ((state[ 4 + i] & 0xeeee) >> 1);
		state[ 8 + i] = ((state[ 8 + i] & 0x3333) << 2)
			| ((state[ 8 + i] & 0xcccc) >> 2);
		state[12 + i] = ((state[12 + i] & 0x7777) << 1)
			| ((state[12 + i] & 0x8888) >> 3);
	}
}

/*
 * Apply the SR_sheet permutation.
 */
static void
SR_sheet(uint16_t *state)
{
	int i;

	for (i = 0; i < 4; i ++) {
		state[ 4 + i] = ((state[ 4 + i] <<  4) | (state[ 4 + i] >> 12));
		state[ 8 + i] = ((state[ 8 + i] <<  8) | (state[ 8 + i] >>  8));
		state[12 + i] = ((state[12 + i] << 12) | (state[12 + i] >>  4));
	}
}

/*
 * Apply the inverse of the SR_sheet permutation.
 */
static void
SR_sheet_inv(uint16_t *state)
{
	int i;

	for (i = 0; i < 4; i ++) {
		state[ 4 + i] = ((state[ 4 + i] << 12) | (state[ 4 + i] >>  4));
		state[ 8 + i] = ((state[ 8 + i] <<  8) | (state[ 8 + i] >>  8));
		state[12 + i] = ((state[12 + i] <<  4) | (state[12 + i] >> 12));
	}
}

/*
 * XOR the key into the state.
 */
static void
XOR_key(const uint16_t *key, uint16_t *state)
{
	int i;
	// xoring all the state blocks with the key blocks
	for (i = 0; i < 16; i ++) {
		state[i] ^= key[i];
	}
}

/*
 * XOR the rotated key into the state.
 */
// in the rounds where rmod4=1, we use this rotated key
// so the key is being right rotated by 4 times
// and we can achieve this by dropping the top 11 bits so the last 4 come to the first 4 
// then we drop the last 5 bits
// so the top 11 become the bottom 11
// and when we combine them we get a 4 right rotated bit array
static void
XOR_key_rotated(const uint16_t *key, uint16_t *state)
{
	int i;
	for (i = 0; i < 16; i ++) {
		state[i] ^= (key[i] << 11) | (key[i] >> 5);
	}
}

/*
 * Perform one Saturnin block encryption.
 *   R     number of super-rounds (0 to 31)
 *   D     separation domain (0 to 15)
 *   key   key (32 bytes)
 *   buf   block to encrypt
 * The 'key' and 'buf' buffers may overlap. The encrypted block is
 * written back in 'buf'.
 */
void
saturnin_block_encrypt(int R, int D, const uint8_t *key, uint8_t *buf)
{
	// arrays of 16 bit round constants
	// for saturnin short, R is 10 and D is 6
	uint16_t RC0[31], RC1[31];

	// xk is the key block
	// xb is the state block
	// an array of size 16 of unsigned 16 bit integer => 16*16 = 256
	uint16_t xk[16], xb[16];

	// global variable for iteration
	int i;

	/*
	 * Decode key and input block buffer and put in xk and xb
	 */
	// for each 16 bit int in xk and xb 
	// there is a low byte and there is a high byte
	// the low byte is key of i*2 and high byte is key of i*2 + 1
	// so for i = 0, key0 and key1 are xk0
	// for i = 1, key2 and key3 are xk1 etc
	for (i = 0; i < 16; i ++) {
		xk[i] = key[i << 1] + ((uint16_t)key[(i << 1) + 1] << 8);
		xb[i] = buf[i << 1] + ((uint16_t)buf[(i << 1) + 1] << 8);
	}

	/*
	 * Compute round constants.
	 * fill the round constant arrays with appropriate round constants
	 */
	make_round_constants(R, D, RC0, RC1);

	/*
	 * XOR key into state.
	 */
	XOR_key(xk, xb);

	/*
	 * Run all rounds (two rounds per super-round).
	 */
	// we are having r = 10 so we are doing 2 rounds per super round
	// one for even and one for odd
	for (i = 0; i < R; i ++) {
		/*
		 * Even round.
		 */
		S_box(xb);
		MDS(xb);
		print_state(xb, "Encrypt", i, "Even");

		/*
		 * Odd round.
		 */
		S_box(xb);
		if ((i & 1) == 0) {
			/*
			 * Round r = 1 mod 4.
			 */
			SR_slice(xb);
			MDS(xb);
			SR_slice_inv(xb);
			xb[0] ^= RC0[i];
			xb[8] ^= RC1[i];
			XOR_key_rotated(xk, xb);
			print_state(xb, "Encrypt", i, "Even");
		} else {
			/*
			 * Round r = 3 mod 4.
			 */
			SR_sheet(xb);
			MDS(xb);
			SR_sheet_inv(xb);
			xb[0] ^= RC0[i];
			xb[8] ^= RC1[i];
			XOR_key(xk, xb);
			print_state(xb, "Encrypt", i, "Even");
		}
	}

	/*
	 * Encode output block.
	 */
	for (i = 0; i < 16; i ++) {
		buf[(i << 1) + 0] = (uint8_t)xb[i];
		buf[(i << 1) + 1] = (uint8_t)(xb[i] >> 8);
	}
}

/*
 * Perform one Saturnin block decryption.
 *   R     number of super-rounds (0 to 31)
 *   D     separation domain (0 to 15)
 *   key   key (32 bytes)
 *   buf   block to decrypt
 * The 'key' and 'buf' buffers may overlap. The decrypted block is
 * written back in 'buf'.
 */
void
saturnin_block_decrypt(int R, int D, const uint8_t *key, uint8_t *buf)
{
	uint16_t RC0[31], RC1[31];
	uint16_t xk[16], xb[16];
	int i;

	/*
	 * Decode key and input block.
	 */
	for (i = 0; i < 16; i ++) {
		xk[i] = key[i << 1] + ((uint16_t)key[(i << 1) + 1] << 8);
		xb[i] = buf[i << 1] + ((uint16_t)buf[(i << 1) + 1] << 8);
	}

	/*
	 * Compute round constants.
	 */
	make_round_constants(R, D, RC0, RC1);

	/*
	 * Run all rounds (two rounds per super-round).
	 */
	for (i = R - 1; i >= 0; i --) {
		/*
		 * Odd round.
		 */
		if ((i & 1) == 0) {
			/*
			 * Round r = 1 mod 4.
			 */
			XOR_key_rotated(xk, xb);
			xb[0] ^= RC0[i];
			xb[8] ^= RC1[i];
			SR_slice(xb);
			MDS_inv(xb);
			SR_slice_inv(xb);
			print_state(xb, "Decrypt", i, "Odd (Slice)");
		} else {
			/*
			 * Round r = 3 mod 4.
			 */
			XOR_key(xk, xb);
			xb[0] ^= RC0[i];
			xb[8] ^= RC1[i];
			SR_sheet(xb);
			MDS_inv(xb);
			SR_sheet_inv(xb);
			print_state(xb, "Decrypt", i, "Odd (Sheet)");
		}
		S_box_inv(xb);

		/*
		 * Even round.
		 */
		MDS_inv(xb);
		S_box_inv(xb);
		print_state(xb, "Decrypt", i, "Even");
	}

	/*
	 * XOR key into state.
	 */
	XOR_key(xk, xb);

	/*
	 * Encode output block.
	 */
	for (i = 0; i < 16; i ++) {
		buf[(i << 1) + 0] = (uint8_t)xb[i];
		buf[(i << 1) + 1] = (uint8_t)(xb[i] >> 8);
	}
}
