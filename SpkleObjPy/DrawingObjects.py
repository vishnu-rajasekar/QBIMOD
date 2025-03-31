import os 
from datetime import datetime

from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.objects import Base
from specklepy.objects.other import Collection

from specklepy.objects.geometry import Point

from specklepy.transports.server import ServerTransport
from specklepy.api.operations import send

import pandas as pd 

#-------------------------------------------------------
# Inputs
#-------------------------------------------------------

excelPath = r"C:\Users\vrajasekar\Downloads\simpleTable.xlsx"
stream_name = "DrawingDatabase"
model_name = "Drawing Model"

#-------------------------------------------------------
# Read excel
#-------------------------------------------------------

output_dir = os.path.dirname(excelPath)

df = pd.read_excel(excelPath)
df = df.where(pd.notnull(df), None)  # Replace NaN with None (optional, good for nulls)
df = df.astype(object)  # This makes each cell a plain Python object instead of numpy dtypes

header = df.head(0)
row_count = df.shape[0]

#-------------------------------------------------------
# Object creation - Many Children
#-------------------------------------------------------
pt = Point(x=0,y=0,z=0)

dwgs = []
for i, row_data in df.iterrows():
    dwg_obj = Base(name=f"@Drawing_{i}")
    dwg_obj["@displayValue"] = pt

    #Assign row data as properties in the Base object
    for col_name in df.columns:
        dwg_obj[col_name] = row_data[col_name]

    dwg_obj["timestamp"] = datetime.utcnow().isoformat()
    dwgs.append(dwg_obj)

drawing_set = Collection(
    name="Drawing Set",
    elements=dwgs
)

#-------------------------------------------------------
# Send to speckle
#-------------------------------------------------------

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


# This is the model/branch
client.branch.create(stream_id, name = model_name, description = "Uploaded drawing objects as a Base object")

transport = ServerTransport(client=client, stream_id=stream_id)

parent_id = send(base=drawing_set, transports=[transport])

commit_id = client.commit.create(
    stream_id=stream_id,
    object_id=parent_id,
    branch_name=model_name,
    message="2 - Drawing Set with Drawing as Base - Hyperlinked"
)
