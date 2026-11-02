"""Public browser export must agree with the existing Python analysis."""
import json
from pathlib import Path
import pytest
from src import kpis
ROOT=Path(__file__).resolve().parents[1]
def payload():return json.loads((ROOT/'docs/assets/data.json').read_text())

def test_web_export_matches_python_engine(df):
    data=payload();rows=data['rows'];n=sum(r[7] for r in rows)
    expected=kpis.on_time_delivery_rate(df)
    assert n==expected['shipments']
    assert sum(r[7] for r in rows if r[4]>0)==expected['delayed']
    assert sum(r[5]*r[7] for r in rows)==kpis.late_delivery_risk_ratio(df)['risk_1']
    assert sum(r[4]*r[7] for r in rows)/n==pytest.approx(kpis.average_delivery_delay(df)['avg_gap_days'],abs=.0005)


def test_web_export_excludes_personal_fields():
    data=payload()
    assert data['columns']==['mode','region','market','segment','gap','risk','canceled','count','sales']
    assert all(len(row)==9 for row in data['rows'])


def test_public_reports_and_media_are_real_files():
    docs=ROOT/'docs'
    for name in ['index.html','project-explanation.html','internship-reflection.html','assets/app.js','assets/style.css','assets/plotly.min.js','.nojekyll']:
        assert (docs/name).is_file()
    assert (docs/'project-report.pdf').read_bytes().startswith(b'%PDF')
    for name in ['project-walkthrough.mp4','internship-reflection-draft.mp4']:
        assert b'ftyp' in (docs/name).read_bytes()[:32]
    assert 'draft' in (docs/'internship-reflection.html').read_text().lower()
