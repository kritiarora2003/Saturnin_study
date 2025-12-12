# 3-Round Differential-Linear Distinguisher

This directory contains a 3-round Differential-Linear (DL) distinguisher for the Toy Saturnin cipher.

## Files

*   `dl_3round.py`: The Python script implementing the distinguisher.

## Structure

The 3-round distinguisher is constructed by chaining three parts:

1.  **Round 1 (Differential $E_0$):**
    *   Input Diff: `[2, 1, 3, 3, 1, 3, 1, 0]`
    *   Output Diff: `[1, 0, 0, 0, 0, 0, 0, 0]`
    *   Probability: $\approx 0.004$

2.  **Round 2 (Interaction $E_m$):**
    *   Input Diff: `[1, 0, 0, 0, 0, 0, 0, 0]`
    *   Output Mask: `[4, 0, 0, 0, 0, 0, 0, 0]`
    *   Bias: $1.0$ (Perfect correlation)

3.  **Round 3 (Linear $E_1$):**
    *   Input Mask: `[4, 0, 0, 0, 0, 0, 0, 0]`
    *   Output Mask: `[0, 0, 8, 0, 0, 0, 0, 0]`
    *   Bias: $\approx 0.076$

## Parameters

*   **Input Difference ($\Delta_{in}$):** `[2, 1, 3, 3, 1, 3, 1, 0]`
*   **Output Mask ($\Gamma_{out}$):** `[0, 0, 8, 0, 0, 0, 0, 0]`

## Performance

The theoretical bias is approximately the product of the component biases (scaled by probability):
$$ \text{Total Bias} \approx Pr(E_0) \times Bias(E_m) \times Bias(E_1) \approx 0.004 \times 1.0 \times 0.076 \approx 0.0003 $$

To detect this small bias, the script uses **2,000,000 trials**.

## Usage

Run the script:

```bash
python3 dl_3round.py
```
