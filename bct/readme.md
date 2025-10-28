# 🌀 Saturnin & PRESENT S-box — Boomerang Connectivity Table (BCT)

This script computes the **Boomerang Connectivity Table (BCT)** for the **Saturnin S-boxes** (`σ₀`, `σ₁`) and the **PRESENT cipher S-box**.

---

## 📘 Overview

The **Boomerang Connectivity Table (BCT)** measures an S-box’s resistance to **boomerang attacks**, a form of advanced differential cryptanalysis.

---

## ⚙️ Features

* Works for any valid permutation S-box
* Computes inverse automatically
* Prints a formatted hex-indexed BCT
* Includes a Makefile for easy running and cleanup

---

## 📁 Folder Structure

```
📁 your_project_folder/
├── saturnin_bct.py     
├── Makefile            
└── bct.png             
```

---

## ▶️ How to Run

You can run the script directly or via the Makefile.

### 🔹 Option 1 — Run with Python

```bash
python3 saturnin_bct.py
```

### 🔹 Option 2 — Run with Makefile

```bash
make run
```

---

## 🧩 Included S-boxes

| Cipher   | Name         | Bits  |
| -------- | ------------ | ----- |
| Saturnin | σ₀           | 4-bit |
| Saturnin | σ₁           | 4-bit |
| PRESENT  | present_sbox | 4-bit |

---

## 🧑‍💻 Author

**Kriti Arora** — Minimal Python tool for analyzing S-box boomerang properties.

