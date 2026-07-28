import pandas as pd
from pathlib import Path
p = Path('Doweighs.xlsx')
df = pd.read_excel(p, engine='openpyxl')
print('COLUMNS:', list(df.columns))
print(df.head(20).to_string(index=False))
print('ROWS', len(df))