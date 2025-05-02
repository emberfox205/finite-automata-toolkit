# finite-automata-toolkit

[![Python](https://img.shields.io/badge/python-3.12.9-blue.svg)](https://www.python.org/downloads/release/python-3129/)

Collection of GUI tools, built with Streamlit, to create and interact with finite automata.

---

## Installation

### Prerequisites

- [Python 3.12.9](https://www.python.org/downloads/release/python-3129/) or newer
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/distribution) (optional)
- [Graphviz](https://graphviz.org/download/) (required for visualization)

### Setup Instructions

1. Clone the repository
   ```bash
   git clone https://github.com/emberfox205/finite-automata-toolkit.git
   cd finite-automata-toolkit
   ```

2. Install Graphviz (system dependency)
   
   **On Windows:**
   ```bash
   # Download and install from https://graphviz.org/download/
   # Make sure to add Graphviz to your PATH during installation
   ```
   
   **On macOS:**
   ```bash
   brew install graphviz
   ```
   
   **On Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install graphviz
   ```

3. Set up environment (choose one option):

   **Option A: Using Python's venv**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

   **Option B: Using Conda (optional)**
   ```bash
   conda create -n finite-automata python=3.12.9
   conda activate finite-automata
   ```

4. Install required dependencies
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application
   ```bash
   streamlit run main.py
   ```
