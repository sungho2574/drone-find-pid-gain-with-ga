import pandas as pd
import numpy as np
df  = pd.read_csv('mass/test.csv')

print(df.dm.values.sum())