# AGENTS.md - Developer Guide for Agents

This document provides essential information for autonomous agents and developers operating within the `Lang2LTL` codebase. It outlines the build system, testing procedures, code style conventions, and project structure to ensure consistent and high-quality contributions.

## 1. Environment & Setup

The project relies on `conda` and `pip` for dependency management. The primary Python version is **3.9**.

### Installation Commands
Agents should assume the environment might need to be set up or updated. Refer to `README.md` for the authoritative source, but the general steps are:

```bash
# Create conda environment
conda create -n lang2ltl python=3.9 dill matplotlib plotly scipy scikit-learn pandas tenacity
conda activate lang2ltl

# Install pip dependencies
pip install openai tiktoken nltk seaborn pyyaml tensorboard transformers datasets evaluate

# Install PyTorch (GPU recommended)
conda install pytorch torchvision torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia
# OR for CPU
# conda install pytorch torchdata -c pytorch

# Install Spot (LTL library)
conda install -c conda-forge spot
```

**Note**: Ensure the `spot` library is correctly installed, as it is critical for LTL formula manipulation.

## 2. Testing & Verification

The project uses the standard `unittest` framework. All tests are consolidated in `tester.py`.

### Running Tests
Agents must verify changes by running relevant tests.

*   **Run All Tests (Regression Check)**:
    ```bash
    python tester.py
    ```

*   **Run a Specific Test Class**:
    ```bash
    python -m unittest tester.TestUtils
    ```

*   **Run a Single Test Case**:
    Use this when debugging a specific function.
    ```bash
    python -m unittest tester.TestUtils.test_substitute_single_letter
    ```

### Adding New Tests
*   New tests should be added to `tester.py` or a new test file if the scope warrants it.
*   Follow the pattern of `TestUtils` class inheriting from `unittest.TestCase`.
*   Use `self.assertEqual` for assertions.

## 3. Code Style & Conventions

Adhere strictly to the existing style found in core files like `utils.py` and `lang2ltl.py`.

### Formatting
*   **Indentation**: Use **4 spaces** per indentation level. Do not use tabs.
*   **Line Length**: Aim for < 120 characters to maintain readability, though some existing lines may exceed this.
*   **Whitespace**:
    *   Two blank lines between top-level functions and classes.
    *   One blank line between methods within a class.
    *   Space after commas in lists/arguments.

### Naming Conventions
*   **Variables & Functions**: `snake_case` (e.g., `input_strs`, `substitute_maps`, `build_placeholder_map`).
*   **Classes**: `CamelCase` (e.g., `TestUtils`, `GPT3`).
*   **Constants**: `UPPER_CASE` (e.g., `BINARY_OPERATORS`, `MAX_SRC_LEN`).
*   **Filenames**: `snake_case` (e.g., `dataset_lifted.py`).

### Documentation
*   **Docstrings**: Use **Sphinx/Google-style** docstrings for functions.
    *   Must include `:param` descriptions and `:return` value.
    *   Example:
        ```python
        def substitute(input_strs, substitute_maps, is_utt):
            """
            Substitute every occurrence of key in the input string.
            
            :param input_strs: List of input strings
            :param substitute_maps: Dictionary mapping substrings to substitutions
            :param is_utt: Boolean, True if input is utterance
            :return: Tuple of (substituted strings, substitutions done)
            """
            ...
        ```

### Typing
*   **No Explicit Type Hints**: The codebase generally does *not* use Python 3 type annotations (e.g., `x: int`).
*   Rely on clear variable names and detailed docstrings to convey type information.

### Imports
*   Order: Standard Library -> Third-Party -> Local Application.
*   Example:
    ```python
    import os
    import json
    import random
    
    import numpy as np
    import nltk
    
    from utils import load_from_file
    ```
*   Avoid `from module import *`.

### Error Handling
*   Raise specific exceptions (e.g., `ValueError`, `FileNotFoundError`) rather than generic `Exception`.
*   Provide informative error messages.
    ```python
    raise ValueError(f"ERROR: unrecognized conversion rule: {convert_rule}")
    ```

## 4. Project Structure & Key Files

*   **`lang2ltl.py`**: Core logic for the Lang2LTL system.
*   **`utils.py`**: Utility functions for string manipulation, file I/O, and data processing. Crucial for helper functions.
*   **`tester.py`**: Main unit test file.
*   **`exp_full.py`**: Main entry point for running experiments.
*   **`gpt.py`**: Wrapper/Interface for OpenAI GPT models.
*   **`dataset_*.py`**: Various scripts for generating and manipulating datasets (lifted, grounded, etc.).
*   **`s2s_hf_transformers.py`**: Script for fine-tuning HuggingFace models (T5, etc.).

## 5. Running Experiments & Common Tasks

### Full Experiment Loop
To run the full evaluation pipeline:
```bash
python exp_full.py --domain osm --envs new_york_1
```

### Common Flags for `exp_full.py`
*   `--domain`: `osm` or `cleanup`
*   `--full_e2e`: `gpt3`, `gpt4` (for end-to-end translation)
*   `--sym_trans`: `t5-base`, `gpt3_finetuned` (for symbolic translation module)
*   `--holdout`: `utt`, `formula`, `type` (for specific test splits)

### Dataset Generation
To generate the lifted dataset (updates existing CSVs):
```bash
python dataset_lifted.py --perm --update --merge
```

### Fine-tuning
To fine-tune a model:
```bash
python s2s_hf_transformers.py --model=t5-base --data <path_to_data>
```

## 6. Git & Version Control

*   **Commit Messages**: Use the format `<type>: <subject>`.
    *   Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`.
    *   Example: `fix: correct token counting logic in utils.py`
*   **Safety**: **NEVER** commit API keys or secrets. Check for `.env` files or hardcoded credentials before committing.
*   **Diffs**: Review `git diff` carefully to ensure only intended changes are included.

## 7. Troubleshooting

*   **Path Issues**: Always use absolute paths or `os.path.join` relative to the script location.
*   **Dependencies**: If `import` errors occur, verify the conda environment is active and `pip install` has been run.
*   **LTL Syntax**: If `spot` fails to parse a formula, ensure the syntax matches Spot's requirements (infix vs prefix, operator symbols).

---
*Created for AI Developer Agents. Refine this file as the project evolves.*
