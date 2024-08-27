# Security Analysis Tools for the Low-Latency First-Order Masked SHA-3  

**Table of Contents:**

- [Introduction](#introduction)
- [Dependencies](#dependencies)
- [Usage](#usage)
  - [Leakage Analysis](#leakage-analysis)
  - [Design Space Search](#design-space-search)
  - [Security Verification](#security-verification)
- [File Structure](#file-structure)
- [Contact](#contact)
- [License](#license)

## Introduction

The software code in this directory is used for security analysis of a first-order masked SHA-3 design, specifically including the following three parts:

- **DOM-Keccak Leakage Analysis**: Code for conducting leakage analysis on the SHA-3 implementation.
- **Design Space Exploration**: Programs for exploring different design configurations.
- **Security Proofs**: Code supporting the theoretical security proofs provided in the paper.

## Dependencies

Our programs are written in **Python**, and each `.py` file can be run directly. We have tested these programs on version 3.11.0. The dependencies for the programs in each directory include:

- `.\security verification\`: Requires `json`
- `.\leakage analysis\`: Requires `json`
- `.\design space search\`: Requires `json`, `tqdm`

## Usage

### Leakage Analysis

- Enter the directory:

  ```
  cd '.\leakage analysis\'
  ```

- To analyze leaks in DOM-Keccak-$f[200]$, run the following command:

  ```
  python dom_f200_leaks.py
  ```

  This will output the detected leaks in the console.

- To analyze leaks in DOM-Keccak-$f[200]$, run the following command:

  ```
  python dom_f1600_leaks.py
  ```

  This will output the probe sets of detected leaks to the console and to a file named `glitch_subsets.json`.

  To analyze whether these sets lead to practical leakage, run the following command:

  ```
  python dom_independence_check.py
  ```
  
  The test results will be printed in the console.

### Design Space Search

- Enter the directory and run:

  ```
  cd '.\design space search\'
  python design_space_search.py
  ```

  The results will be save in a file named `search_results.log`.

  Please note that we have omitted certain security checks to speed up the search, so the results cannot be guaranteed to be secure. Please run all programs in the `security verification` folder to ensure security.

- This program uses multiple cores for acceleration. You can modify the number of cores used by adjusting the `n_cores` variable at the beginning of the file `design_space_search.py`.

- Running this program on a laptop with 10 cores takes approximately 29 minutes.

### Security Verification

- Enter the directory:

  ```
  cd '.\security verification\'
  ```

- To verify glitch-robust probing security,

  - Generate glitch-extended probing index list:

    ```
    python glitch_list_generation.py
    ```

    The lists will be save in a file named `glitch_list.json`

  - Check the non-completeness of the first round:

    ```
    python glitch_first_round_non_completeness.py
    ```

    The test results will be printed in the console.

  - Check uniformity of $(\hat v^{n-1}[\dots],\hat s'^{n-1}[\dots])$ for each glitch-extended probe:

    ```
    python glitch_ct_uniform_proofs_generation.py
    ```

    This will generate proof steps of the uniformity into a file named `glitch_ct_uniform_proofs.json`, which can be read by `ct_uniform_proofs_reader.py`:

    ```
    python ct_uniform_proofs_reader.py glitch_ct_uniform_proofs.json x y z s
    ```

    where, `x`, `y`, `z`, and `s` are the indices of the glitch-robust probe. For example, to view the uniform proof steps of $(\hat v^{n-1}[\dots],\hat s'^{n-1}[\dots])$ corresponding to the probe on $d^n_3[0,2,45]$:

    ```
    python ct_uniform_proofs_reader.py glitch_ct_uniform_proofs.json 0 2 45 3
    ```

  - Partition index lists into independent subsets:

    ```
    python glitch_partition_subsets.py
    ```

    This will save classified subsets into a file named `glitch_subsets.json`.

    Check independence of register values and secret values for each subset:

    ```
    python glitch_independence_check.py
    ```

    The test results will be printed in the console.

- To verify glitch+register-transition-robust probing security

  ```
  python glitch_list_generation.py
  python glitch+trans_ct_uniform_proofs_generation.py
  python glitch+trans_partition_subsets.py
  python glitch+trans_independence_check.py
  ```

  To view the uniform proof steps of $(\hat v^{n-1}[\dots],\hat s'^{n-1}[\dots])$ corresponding to the probe on $d^n_3[0,2,45]$:

  ```
  python ct_uniform_proofs_reader.py glitch+trans_ct_uniform_proofs.json 0 2 45 3
  ```

## File Structure

- `.\leakage analysis\`:  Leakage analysis codes for DOM-Keccak, used in **Section 3** of the paper.
  - `dom_f200_leaks.py`:  Used for examining leaks resulting from non-completeness violations in DOM-Keccak-$f[200]$.
  - `dom_f1600_leaks.py`:  Used for examining leaks resulting from non-completeness violations and new leaks reported in the paper in DOM-Keccak-$f[1600]$.
    - `glitch_subsets.json`: Output file, used by `dom_independence_check.py`.
  - `dom_independence_check.py`: DOM-Keccak version of **Algorithm 4**, checking independence of register values and secret values. 
- `.\design space search\`: Design space search codes, used in **Section 3.4** of the paper.
  - `design_space_search.py`: Parallel search for available design parameters.
    - `search_results.log`: Output file.
- `.\security verification\`: Security verification algorithm codes, used in **Section 5** of the paper.
  - `glitch_list_generation.py`: **Algorithm 1** used in **Section 5** of the paper. Glitch-extended probing index list generation.  
    - `glitch_list.json`: Output of `glitch_list_generation.py`, used by `glitch_first_round_non_completeness.py`, `glitch_ct_uniform_proofs_generation.py` and `glitch_partition_subsets.py`.
  - `glitch_first_round_non_completeness.py`: Checking the non-completeness of the first round, used in **Section 5.1** of the paper
  - `glitch_ct_uniform_proofs_generation.py`: **Algorithm 2** used in **Section 5.2** of the paper. Checking uniformity of $(\hat c,\hat t)$ for each glitch-extended probe.  
    - `glitch_ct_uniform_proofs.json`: Output of `glitch_ct_uniform_proofs_generation.py`, saving the proof steps, can be read by `ct_uniform_proofs_reader.py`.
  - `glitch_partition_subsets.py`: **Algorithm 3** used in **Section 5.2** of the paper. Partitioning index lists into independent subsets.
    - `glitch_subsets.json`: Output of `glitch_partition_subsets.py`, used by `glitch_independence_check.py`.
  - `glitch_independence_check.py`: **Algorithm 4** used in **Section 5.2** of the paper. Checking independence of register vaulues and secret values for each subset.  
  - `glitch+trans_ct_uniform_proofs_generation.py`:  **Algorithm 2** used in **Section 5.3** of the paper, considering combined first-order glitch-robust and register transition-robust model.
    - `glitch+trans_ct_uniform_proofs.json`: Output file.
  - `glitch+trans_partition_subsets.py`: **Algorithm 3** used in **Section 5.3** of the paper, considering combined first-order glitch-robust and register transition-robust model.
    - `glitch+trans_subsets.json`: Output file.
  - `glitch+trans_independence_check.py`: **Algorithm 4** used in **Section 5.3** of the paper.
  - `ct_uniform_proofs_reader.py`: Used to read the proofs `glitch_ct_uniform_proofs.json` and `glitch+trans_ct_uniform_proofs.json`.

## Contact

Please contact [Cankun Zhao](https://github.com/zck15) ([zck22@mails.tsinghua.edu.cn](mailto:zck22@mails.tsinghua.edu.cn)) if you have any questions, comments, if you found a bug that should be corrected, or if you want to reuse the codes or parts of them for your own research projects.

## License

Copyright (c) 2024, Cankun Zhao, Leibo Liu. All rights reserved.

Please see `..\LICENSE` for further license instructions.