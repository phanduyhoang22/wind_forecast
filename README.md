# wind_forecast
A Comparative Study of State Space Models, Attention Mechanisms, and Traditional Machine Learning for Short-Term Wind Speed Forecasting.

# Short-Term Wind Speed Forecasting using Mamba, Transformer, LSTM, and Random Forest
This repository contains the source code, datasets, and experiment notebooks for the research paper: *"A High-Efficiency Mamba Framework for Explainable Multi-Site Short-Term Wind Speed Forecasting"*.

## Datasets
The data includes multivariate meteorological features (Wind Speed, Temperature, Pressure, etc.) collected at 15-minute intervals across 4 diverse topographic regimes:
* `Tram_A_DatLien_FINAL_MASTER.csv`: Inland regime.
* `Tram_B_VenBien_FINAL_MASTER.csv`: Coastal regime.
* `Tram_C_DoiNui_FINAL_MASTER.csv`: Complex/Mountainous terrain.
* `Tram_D_NgoaiKhoi_FINAL_MASTER.csv`: Offshore regime.

## Models Implemented
* **Random Forest (RF.ipynb):** Serves as a robust baseline and provides feature selection via TreeSHAP.
* **LSTM (LS.ipynb):** Effectively models short-term temporal dependencies.
* **Transformer (TFM.ipynb):** Utilizes self-attention for long-range context modeling.
* **Mamba (MB.ipynb):** A state-space model offering linear-time complexity with Transformer-level accuracy.
