from specklepy.objects import Base 
from specklepy.api import operations
import pandas as pd 
import os 

excelPath = r"C:\Users\vrajasekar\Downloads\simpleTable.xlsx"
output_dir = os.path.dirname(excelPath)

df = pd.read_excel(excelPath)

print(df)