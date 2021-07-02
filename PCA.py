from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pandas_datareader.data as pdr
from datetime import datetime

start = datetime(2000, 1, 1)
end = datetime(2018,4,2)
treasury_df = pdr.DataReader(["DGS1", "DGS2", "DGS3", "DGS5", "DGS7", "DGS10"], "fred", start, end)



treasury_df.plot(figsize=(10,5))
plt.ylabel("Rate")
plt.legend(bbox_to_anchor=(1.01,.9), loc=2)
plt.show()