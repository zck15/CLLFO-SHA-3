## Repository Overview

Welcome to the source code repository for the paper **[Breaking Ground: A New Area Record for Low-Latency First-Order Masked SHA-3]()**, published in *[TCHES 2024 Issue 4]()*. This repository contains all the code and resources necessary to reproduce the results presented in the paper.

**Table of Contents:**

- [Repository Overview](#repository-overview)
  - [Paper Abstract](#paper-abstract)
  - [Authors and Affiliations](#authors-and-affiliations)
- [Repository Content](#repository-content)
- [Contact](#contact)
- [License](#license)

### Paper Abstract

[SHA-3](https://csrc.nist.gov/pubs/fips/202/final), the latest hash standard from NIST, is utilized by numerous cryptographic algorithms to handle sensitive information. Consequently, SHA-3 has become a prime target for side-channel attacks, with numerous studies demonstrating successful breaches in unprotected implementations. Masking, a countermeasure capable of providing theoretical security, has been explored in various studies to protect SHA-3. However, masking for hardware implementations may significantly increase area costs and introduce additional delays, substantially impacting the speed and area of higher-level algorithms. In particular, current low-latency first-order masked SHA-3 hardware implementations require more than four times the area of unprotected implementations. To date, the specific structure of SHA-3 has not been thoroughly analyzed for exploitation in the context of masking design, leading to difficulties in minimizing the associated area costs using existing methods.

We bridge this gap by conducting detailed leakage path and data dependency analyses on two-share masked SHA-3 implementations. Based on these analyses, we propose **a compact and low-latency first-order SHA-3 masked hardware implementation**, requiring only **three times the area of unprotected implementations** and **almost no fresh random number demand**. We also present a complete theoretical security proof for the proposed implementation in the **glitch+register-transition-robust probing model**. Additionally, we conduct leakage detection experiments using PROLEAD, TVLA and VerMI to complement the theoretical evidence. Compared to state-of-the-art designs, our implementation achieves a **28% reduction in area consumption**. Our design can be integrated into first-order implementations of higher-level cryptographic algorithms, contributing to a reduction in overall area costs.

### Authors and Affiliations

- **[Cankun Zhao](https://zck15.github.io/about.html)**[![ORCID](https://orcid.org/sites/default/files/images/orcid_16x16.png)](https://orcid.org/0000-0002-6875-3557), [BNRist](https://www.bnrist.tsinghua.edu.cn/bnristen/About1/Introduction.htm), [SIC](https://www.sic.tsinghua.edu.cn/en/About/Introduction.htm), Tsinghua University, Beijing, China
- **Hang Zhao**, [BNRist](https://www.bnrist.tsinghua.edu.cn/bnristen/About1/Introduction.htm), [SIC](https://www.sic.tsinghua.edu.cn/en/About/Introduction.htm), Tsinghua University, Beijing, China
- **Jiangxue Liu**, [BNRist](https://www.bnrist.tsinghua.edu.cn/bnristen/About1/Introduction.htm), [SIC](https://www.sic.tsinghua.edu.cn/en/About/Introduction.htm), Tsinghua University, Beijing, China
- **[Bohan Yang](https://byang.xyz/)**[![ORCID](https://orcid.org/sites/default/files/images/orcid_16x16.png)](https://orcid.org/0000-0002-5204-1707), [BNRist](https://www.bnrist.tsinghua.edu.cn/bnristen/About1/Introduction.htm), [SIC](https://www.sic.tsinghua.edu.cn/en/About/Introduction.htm), Tsinghua University, Beijing, China
- **Wenping Zhu**, [BNRist](https://www.bnrist.tsinghua.edu.cn/bnristen/About1/Introduction.htm), [SIC](https://www.sic.tsinghua.edu.cn/en/About/Introduction.htm), Tsinghua University, Beijing, China
- **Shuying Yin**, [BNRist](https://www.bnrist.tsinghua.edu.cn/bnristen/About1/Introduction.htm), [SIC](https://www.sic.tsinghua.edu.cn/en/About/Introduction.htm), Tsinghua University, Beijing, China
- **Min Zhu**, [MUCSE](https://mucse.com/en/about/about.aspx), Wuxi, China
- **[Shaojun Wei](https://www.sic.tsinghua.edu.cn/en/info/1083/1444.htm)**, [BNRist](https://www.bnrist.tsinghua.edu.cn/bnristen/About1/Introduction.htm), [SIC](https://www.sic.tsinghua.edu.cn/en/About/Introduction.htm), Tsinghua University, Beijing, China
- **[Leibo Liu](https://www.sic.tsinghua.edu.cn/en/info/1072/1452.htm)**[![ORCID](https://orcid.org/sites/default/files/images/orcid_16x16.png)](https://orcid.org/0000-0001-7548-4116), [BNRist](https://www.bnrist.tsinghua.edu.cn/bnristen/About1/Introduction.htm), [SIC](https://www.sic.tsinghua.edu.cn/en/About/Introduction.htm), Tsinghua University, Beijing, China

## Repository Content

This repository is divided into two main sections: hardware and software.

- **Hardware Implementation**:
   - **RTL Code**: Implementation of the proposed SHA-3 design.
   - **Functional Simulation Scripts**: Scripts to perform functional simulations of the hardware design.
   - **Synthesis Scripts**: Scripts for synthesizing the hardware implementation.
- **Security Analysis Tools**:
   - **DOM-Keccak Leakage Analysis**: Code for conducting leakage analysis on the SHA-3 implementation.
   - **Design Space Exploration**: Programs for exploring different design configurations.
   - **Security Proofs**: Code supporting the theoretical security proofs provided in the paper.

Detailed instructions and usage information for each part can be found in the README files within the respective subdirectories.

## Contact

Please contact [Cankun Zhao](https://github.com/zck15) ([zck22@mails.tsinghua.edu.cn](mailto:zck22@mails.tsinghua.edu.cn)) if you have any questions, comments, if you found a bug that should be corrected, or if you want to reuse the codes or parts of them for your own research projects.

## License

Copyright (c) 2024, Cankun Zhao, Leibo Liu. All rights reserved.

Please see `LICENSE` for further license instructions.

