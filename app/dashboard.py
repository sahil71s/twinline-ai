from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import json
import pandas as pd
import streamlit as st
from simulation.simulator import run_simulation
from simulation.config import SimulationConfig
from analytics.pipeline import run_analytics
from analytics.genealogy import trace_defect
from analytics.what_if import simulate_intervention
from validation.backtest import run_backtest

st.set_page_config(page_title='TwinLine.ai', layout='wide')

DATA = ROOT/'data/generated'
OUT = ROOT/'outputs'

@st.cache_data(show_spinner=False)
def load_all():
    return (pd.read_csv(DATA/'station_catalog.csv'), pd.read_csv(DATA/'production_observations.csv'), pd.read_csv(DATA/'quality_inspections.csv'))

def ensure_data():
    if not (DATA/'production_observations.csv').exists():
        run_simulation('hidden_degradation', SimulationConfig(n_units=300))
        # simulator writes only when called from CLI, so save explicitly

def generate(scenario, units=300):
    stations, vehicles, obs, inspections, maintenance, truth, events = run_simulation(scenario, SimulationConfig(n_units=units))
    DATA.mkdir(parents=True, exist_ok=True)
    stations.to_csv(DATA/'station_catalog.csv', index=False); vehicles.to_csv(DATA/'vehicles.csv', index=False)
    obs.to_csv(DATA/'production_observations.csv', index=False); inspections.to_csv(DATA/'quality_inspections.csv', index=False)
    maintenance.to_csv(DATA/'maintenance_events.csv', index=False); truth.to_csv(DATA/'ground_truth.csv', index=False); events.to_csv(DATA/'vehicle_events.csv', index=False)
    run_analytics(DATA, OUT); run_backtest(DATA, OUT)
    st.cache_data.clear()

st.title('TwinLine.ai')
st.caption('Predict the problem. Trace who it touched. Simulate the decision. Keep the human in control.')

with st.sidebar:
    st.header('Twin Controls')
    scenario = st.selectbox('Scenario', ['hidden_degradation','bottleneck','sensor_gap','normal'])
    units = st.number_input('Vehicles', min_value=100, max_value=1000, value=300, step=100)
    if st.button('Run scenario', type='primary'):
        with st.spinner('Simulating line...'):
            generate(scenario, int(units))
        st.success('Scenario generated.')
    page = st.radio('View', ['Line Overview','Station Detail','Defect Genealogy','What-If Simulator','Validation & ROI'])

try:
    stations, obs, inspections = load_all()
except Exception:
    st.info('Run a scenario from the sidebar to create the prototype dataset.')
    st.stop()

scored_path = OUT/'scored_observations.csv'
if not scored_path.exists():
    run_analytics(DATA, OUT); run_backtest(DATA, OUT)
scored = pd.read_csv(scored_path)

if page == 'Line Overview':
    st.subheader('1 · Line Overview — Floor Supervisor')
    latest = scored.sort_values('completion_min').groupby('station_id').tail(1).merge(stations[['station_id','station_name','stage','sensor_tier']], on='station_id', suffixes=('','_meta'))
    latest['status'] = latest['predicted_defect_risk'].apply(lambda x: '🔴 HIGH' if x >= .65 else ('🟠 WATCH' if x >= .35 else '🟢 NORMAL'))
    st.dataframe(latest[['station_id','station_name','stage','sensor_tier','status','predicted_defect_risk','bottleneck_risk','queue_length','cycle_time_s','confidence_tier']].sort_values('station_id'), use_container_width=True, hide_index=True)
    c1,c2,c3 = st.columns(3); c1.metric('Stations', len(stations)); c2.metric('Vehicles', scored.vehicle_id.nunique()); c3.metric('Manual-only stations', int((stations.sensor_tier=='manual').sum()))
    st.info('OT integration is read-only/passive. The prototype never writes to PLC logic.')

elif page == 'Station Detail':
    st.subheader('2 · Station Detail + Prediction')
    sid = st.selectbox('Station', stations.station_id.tolist(), format_func=lambda x: f'ST-{x:02d}')
    s = scored[scored.station_id==sid].sort_values('completion_min')
    meta = stations[stations.station_id==sid].iloc[0]
    latest = s.tail(1).iloc[0]
    c1,c2,c3,c4 = st.columns(4); c1.metric('Defect risk', f'{latest.predicted_defect_risk:.0%}'); c2.metric('Bottleneck risk', f'{latest.bottleneck_risk:.0%}'); c3.metric('Confidence', latest.confidence_tier); c4.metric('Sensor tier', meta.sensor_tier.upper())
    st.write(f"**Evidence signals:** SPC alarms = {int(latest.spc_alarm_count)}, queue = {latest.queue_length:.1f}, cycle time = {latest.cycle_time_s:.1f}s, upstream defect signal = {latest.upstream_defect_signal:.3f}.")
    st.line_chart(s.set_index('completion_min')[['cycle_time_s','queue_length']].tail(120))
    st.caption('For partial/manual stations, risk is explicitly marked as inferred and confidence is reduced; no synthetic sensor reading is fabricated.')

elif page == 'Defect Genealogy':
    st.subheader('3 · Defect Genealogy Tracer')
    bad = inspections[inspections.defect_flag==1].vehicle_id.unique().tolist()
    if not bad:
        st.warning('No defect found in this scenario. Use hidden_degradation for the signature demo.')
    else:
        vin = st.selectbox('Defect vehicle', bad)
        if st.button('Trace origin', type='primary'):
            result = trace_defect(vin, inspections, scored, stations, snapshot_min=155.5)
            st.json(result)
            st.success(f"Recommended action: {result['recommended_action']}")
            st.write('This trace is deterministic: vehicle history + station graph + observed risk evidence. The LLM is not used as numerical truth.')

elif page == 'What-If Simulator':
    st.subheader('4 · What-If Simulator — Human-in-the-Loop')
    summary = scored.groupby(['station_id','station_name'], as_index=False).agg(risk_score=('predicted_defect_risk','mean'), queue_avg=('queue_length','mean'))
    actions = ['continue','repair_station','quarantine','full_line_stop']
    chosen = st.selectbox('Intervention', actions)
    target = st.selectbox('Target station', stations.station_id.tolist(), index=min(11,len(stations)-1))
    result = simulate_intervention(summary, chosen, int(target))
    st.table(pd.DataFrame([result]))
    st.warning('Recommendation is decision support only. A human must approve or override.')
    decision = st.radio('Human decision', ['APPROVE','OVERRIDE'])
    if st.button('Log decision'):
        OUT.mkdir(exist_ok=True)
        with open(OUT/'decision_log.jsonl','a',encoding='utf-8') as f: f.write(json.dumps({'action':chosen,'target_station':int(target),'decision':decision})+'\n')
        st.success(f'Decision logged: {decision}')

else:
    st.subheader('5 · Validation & ROI — Plant Manager / Leadership')
    mpath = OUT/'backtest_metrics.json'
    metrics = json.loads(mpath.read_text()) if mpath.exists() else run_backtest(DATA, OUT)
    d = metrics['defect']; l = metrics['lead_time_min']
    c1,c2,c3,c4 = st.columns(4); c1.metric('Precision',f"{d['precision']:.0%}"); c2.metric('Recall',f"{d['recall']:.0%}"); c3.metric('False-positive rate',f"{d['false_positive_rate']:.1%}"); c4.metric('Median lead time',f"{l['median']:.1f} min")
    st.write('**Important:** these are synthetic backtest results, not real factory performance claims.')
    st.markdown('### Illustrative ROI')
    minutes = st.number_input('Minutes saved per caught incident', 17, 60, 17)
    incidents = st.number_input('Incidents/week', 1, 10, 2)
    cost = st.number_input('Assumed cost/minute ($)', 1000, 50000, 22000)
    st.metric('Illustrative avoided stoppage/week', f'${minutes*incidents*cost:,.0f}')
    st.caption('Directional assumption only; validate plant-specific economics before use.')
