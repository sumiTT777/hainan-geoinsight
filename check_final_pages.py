from pathlib import Path
from streamlit.testing.v1 import AppTest
app=AppTest.from_file(Path('app.py').resolve(),default_timeout=240).run()
assert not app.exception and not app.error
assert app.metric[3].label=='Walkable Grid Coverage'
for page in ['Regional Comparison','Research Report']:
 app.sidebar.radio[0].set_value(page).run()
 assert not app.exception and not app.error
 print(page,'passed',flush=True)
