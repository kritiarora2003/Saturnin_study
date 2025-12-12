# 🪐 Saturnin Study 🪐

Welcome to the **Saturnin Study** repository! 🎉

This collection of code, tools, and documentation was created as part of a term paper for the **Lightweight Cryptography** course, taught by **Dr. Dhiman Saha**. Here, we dive deep into the **Saturnin** block cipher, exploring its implementation, security, and inner workings.

Whether you're here to check out the code, run some attacks, or just learn more about lightweight crypto, we hope you find this resource helpful and interesting! 🚀

## 📂 Directory Structure

### 🛠️ Implementation
- **`implementation/`**: The heart of the project! Contains the reference implementation of Saturnin in C and Python. Includes a `makefile` and test vectors to get you started.
- **`toy/`**: A simplified "toy" version of the cipher. Perfect for understanding the core concepts without getting lost in the full complexity. Check out the Jupyter notebook!

### 🕵️‍♀️ Cryptanalysis
- **`diff_lin/`**: Dive into **Differential-Linear Cryptanalysis** with our scripts and 3-round distinguishers.
- **`boomerang_saturnin/`**: See **Boomerang Attacks** in action against Saturnin.
- **`linear_cryptanalysis/`**: Resources for linear cryptanalysis, including the Linear Approximation Table (LAT).
- **`zerosum/`**: Explore **Zero-Sum Distinguishers** and algebraic degree analysis.
- **`bct/`**: Tools for generating the Boomerang Connectivity Table (BCT), Difference Distribution Table (DDT), and Boomerang Difference Table (BDT).
- **`ddt/`**: Scripts for analyzing the Difference Distribution Table (DDT).
- **`ANF/`**: For the hardware enthusiasts! Resources related to **Algebraic Normal Form (ANF)** analysis, synthesis reports, and Verilog files.

### 🤖 Automated Tools
- **`milp/`**: Harness the power of **Mixed Integer Linear Programming (MILP)** for cryptanalysis. Includes S-box hull inequalities and Gurobi scripts.
- **`mzn/`**: **MiniZinc** models for constraint programming-based analysis.

### 📚 Documentation & Presentation
- **`termpaper/`**: The "PhinisheD" product! LaTeX source files for the thesis/term paper, neatly organized by chapters.
- **`saturnin_ppt/`**: Slides and resources for the project presentation.

### 🧪 Miscellaneous
- **`Brownie_server/`**: A client-server setup, possibly for distributed tasks or specific attack scenarios. Also features an implementation of the **Twinkle** cipher components.

## 🚀 Getting Started
Ready to explore? Head over to the `README.md` files within specific subdirectories (like `implementation/` or `milp/`) for detailed instructions on running the tools and experiments.

Happy Hacking! 💻🔐
