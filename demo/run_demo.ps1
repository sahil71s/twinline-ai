python -m simulation.run_simulation --scenario hidden_degradation --units 300
python -c "from analytics.pipeline import run_analytics; print(run_analytics())"
python -m validation.run_validation
streamlit run app/dashboard.py
