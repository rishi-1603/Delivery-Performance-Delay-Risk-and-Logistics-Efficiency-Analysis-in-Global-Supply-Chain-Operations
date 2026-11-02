"""Export a de-identified browser companion dataset from the existing pipeline.
Run from the repository root: python scripts/build_web_data.py [--raw PATH]
The original Streamlit app and metric engine remain the primary Python implementation.
"""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src import config as C
from src.data_cleaning import load_raw,clean
from plotly.offline import get_plotlyjs
parser=argparse.ArgumentParser();parser.add_argument('--raw',default=str(C.RAW_CSV));args=parser.parse_args()
df,log=clean(load_raw(args.raw))
assets=ROOT/'docs/assets';assets.mkdir(exist_ok=True,parents=True)
from src.kpis import on_time_delivery_rate,average_delivery_delay,late_delivery_risk_ratio
keys=[C.COL_SHIP_MODE,C.COL_REGION,C.COL_MARKET,C.COL_SEGMENT,C.COL_GAP,C.COL_RISK,C.COL_CANCELED]
cube=df.groupby(keys,dropna=False).agg(n=(C.COL_GAP,'size'),sales=(C.COL_SALES,'sum')).reset_index()
cube[C.COL_CANCELED]=cube[C.COL_CANCELED].astype(int);cube['sales']=cube.sales.round(4)
expected={**on_time_delivery_rate(df),**average_delivery_delay(df),**late_delivery_risk_ratio(df),'sales':round(float(df[C.COL_SALES].sum()),2)}
result={'kind':'delivery','columns':['mode','region','market','segment','gap','risk','canceled','count','sales'],'rows':cube.values.tolist(),'expected':expected,'source_rows':len(df),'privacy':'Aggregated counts and sales only; no customer names, IDs, addresses or coordinates.'}
(assets/'data.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(assets/'plotly.min.js').write_text(get_plotlyjs(),encoding='utf-8')
print(json.dumps({'source_rows':len(df),'browser_rows':len(result['rows']),'expected':result['expected']},indent=2))
