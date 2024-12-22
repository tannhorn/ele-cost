# LCOE calculator

## Overview

This project is a Python-based tool for calculating the Levelized Cost of Electricity (LCOE) using data and methodology from the International Energy Agency (IEA) and the Organisation for Economic Co-operation and Development/Nuclear Energy Agency (OECD/NEA).

The data used for this project is sourced from the [IEA/OECD-NEA report](https://iea.blob.core.windows.net/assets/ae17da3d-e8a5-4163-a3ec-2e6fb0b5677d/Projected-Costs-of-Generating-Electricity-2020.pdf) titled "Projected Costs of Generating Electricity 2020," which provides comprehensive data on the projected costs of various electricity generation technologies.

## Features

- Calculate the LCOE according to the above methodology

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/Tannhorn/ele-cost.git
   cd ele-cost
   ```

1. Navigate to the project directory:
    ```bash
    cd ele-cost

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Notebook

See the `example.ipynb` notebook. You can run it locally or online for example in Google Colab: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tannhorn/ele-cost/blob/main/example.ipynb)

### Applet

You can run the applet locally or deployed on the cloud.

- To run it locally:
 ```bash
 streamlit run app.py
 ```
This will start a local server. Open the link in your browser (usually `http://localhost:8501`).

- The cloud deployment is not active at the moment.

