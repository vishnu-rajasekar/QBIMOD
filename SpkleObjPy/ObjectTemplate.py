import os 

from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.objects import Base

from specklepy.transports.server import ServerTransport
from specklepy.api.operations import send

import pandas as pd 

# Inputs

excelPath = r"C:\Users\vrajasekar\Downloads\simpleTable.xlsx"

# Read excel
stream_name = "Dwg Database"
output_dir = os.path.dirname(excelPath)

df = pd.read_excel(excelPath)
df = df.where(pd.notnull(df), None)  # Replace NaN with None (optional, good for nulls)
df = df.astype(object)  # This makes each cell a plain Python object instead of numpy dtypes

header = df.head(0)
row_count = df.shape[0]

# Object creation

dwg_objs = {}
for i in range(row_count):
    key = f"dObj{i}"
    dwg_objs[key] = Base()
    for h in header:
        dwg_objs[key][h] = df.iloc[i][h]

print(dwg_objs['dObj2']['BIM 360 PDF Link'])

# Send to speckle

client = SpeckleClient(host="https://app.speckle.systems/")
account = get_default_account()
client.authenticate_with_account(account)

# Get a list of your recent streams
stream_list = client.stream.list()
if not stream_list:
    print("No streams found.")
else:
    print("Streams found:", [s.name for s in stream_list])

# Search for the stream by name
streams_found = client.stream.search(stream_name)
if not streams_found:
    raise ValueError(f"Stream with name '{stream_name}' not found.")
stream = streams_found[0]
stream_id = stream.id
print("Using stream:", stream.name, "with id:", stream_id)

client.branch.create(stream_id, name = "BaseDwgObjs", description = "Uploaded drawing objects as a Base object")

transport = ServerTransport(client=client, stream_id=stream_id)
parent = Base()
parent.elements = list(dwg_objs.values())


object_id = send(base=parent, transports=[transport])
commit_id = client.commit.create(
    stream_id=stream_id,
    object_id=object_id,
    branch_name="BaseDwgObjs",
    message="Uploaded dwg_objs as strings"
)
