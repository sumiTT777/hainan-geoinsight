from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_real_default():
 app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=180).run()
 assert not app.exception and not app.error
 assert all(x.label!='Data mode' for x in app.sidebar.selectbox)
 assert int(app.metric[0].value)>10000
 assert not any('DEMO' in str(w.value) for w in app.warning)
