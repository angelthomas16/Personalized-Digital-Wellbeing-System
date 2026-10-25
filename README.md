# Personalized-Digital-Wellbeing-System

Personalized digital lifestyle and well-being intelligence using smartphone usage data



A personalized digital lifestyle and well-being intelligence system that analyzes smartphone usage data and presents wellbeing insights through an interactive Streamlit dashboard.



\#Features

\- Smartphone usage and wellbeing analytics

\- Personalized wellbeing scores

\- Daily wellbeing trends and digital habit visualizations

\- Detection of unusual usage patterns

\- Recommendations based on usage insights

\- CSV export from the dashboard



\#Requirements

\- Python 3

\- Git



\#Setup



Clone the repository and open its project folder.



Install the required Python packages:



```bash

python -m pip install pandas numpy matplotlib seaborn scikit-learn nbformat ipython streamlit

```



\#Generate Analytics Results



Run the analytics notebook through the helper script:



```bash

python run\_analytics.py

```



The script executes `notebooks/Analytics\_and\_Scoring.ipynb` and generates the analytics outputs in the `results/` directory.



The dashboard requires these files:

\- results/digital\_wellbeing\_scored.csv

\- results/wellbeing\_scores\_daily.csv



These generated CSV files are excluded from Git because of their size. Generate them before launching the dashboard.



\#Launch the Dashboard



python -m streamlit run app.py



Streamlit will display a local URL in the terminal. Open that URL in your browser to use the dashboard.



