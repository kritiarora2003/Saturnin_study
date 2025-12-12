# Differential-Linear Distinguisher for Toy Saturnin

This directory contains a simple 1-round Differential-Linear (DL) distinguisher for the Toy Saturnin cipher.

## Files

*   `dl_distinguisher.py`: The Python script implementing the distinguisher.

## Theory

A Differential-Linear distinguisher combines a differential characteristic ($E_0$) with a linear approximation ($E_1$).
For 1 round, we look for a high correlation between an input difference $\Delta_{in}$ and an output linear mask $\Gamma_{out}$.

We define the bias $\epsilon$ as:
$$ \epsilon = 2 \cdot \Pr[\Gamma_{out} \cdot E(x) = \Gamma_{out} \cdot E(x \oplus \Delta_{in})] - 1 $$

## The Distinguisher

We found a strong distinguisher for 1 round of Toy Saturnin:

*   **Input Difference ($\Delta_{in}$):** `[1, 0, 0, 0, 0, 0, 0, 0]` (Difference `0x1` in the first nibble)
*   **Output Mask ($\Gamma_{out}$):** `[4, 0, 0, 0, 0, 0, 0, 0]` (Mask `0x4` in the first nibble)

This pair exhibits a **bias of 1.0** (Probability 1.0), meaning the masked output bits are always equal for the pair.

## Usage

Run the script:

```bash
python3 dl_distinguisher.py
```
