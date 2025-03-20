import os 

from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.objects import Base

from specklepy.transports.server import ServerTransport
from specklepy.api.operations import send

import pandas as pd 

#-------------------------------------------------------
# Inputs
#-------------------------------------------------------

excelPath = r"C:\Users\vrajasekar\Downloads\simpleTable.xlsx"
stream_name = "Dwg Database"

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
# Object creation
#-------------------------------------------------------

# Dictionary but dwg_objs go into a "element" property of the Base

# dwg_objs = {}
# for i in range(row_count):
#     key = f"dObj{i}"
#     dwg_objs[key] = Base()
#     for h in header:
#         dwg_objs[key][h] = df.iloc[i][h]

# print(dwg_objs['dObj2']['BIM 360 PDF Link'])

# STEP 2: Create a parent Base object
parent = Base()

# Prepare a list for child objects (or store them directly in a property named e.g. "elements").
# child_objects = []

# STEP 3: Convert each row into a separate Base (child) object
for i, row_data in df.iterrows():
    child = Base()
    # Optionally, give it a custom speckle_type (not strictly required)
    child.speckle_type = "Base"

    # Assign row data as properties in the Base object
    for col_name in df.columns:
        child[col_name] = row_data[col_name]

    parent[f"@child_{i}"] = child

    # Collect the child object in a list
    # child_objects.append(child)

# Attach all children to parent in a property called "elements"
# parent.elements = child_objects

# parent["@elements"] = child_objects
# parent.speckle_type = "Base"
# parent.add_detachable_attrs("element")
# parent.add_detachable_attrs("elements", child_objects)

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

# This is the model/branch
client.branch.create(stream_id, name = "BaseDwgObjs", description = "Uploaded drawing objects as a Base object")

transport = ServerTransport(client=client, stream_id=stream_id)

# parent = Base()
# parent.elements = list(dwg_objs.values())
# object_id = send(base=parent, transports=[transport])

parent_id = send(base=parent, transports=[transport])


commit_id = client.commit.create(
    stream_id=stream_id,
    object_id=parent_id,
    branch_name="BaseDwgObjs",
    message="Uploaded detached child as queriable children"
)
