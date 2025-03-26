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
stream_name = "CollectionProject"
model_name = "BaseTest"
#-------------------------------------------------------
# Read excel
#-------------------------------------------------------

output_dir = os.path.dirname(excelPath)

df = pd.read_excel(excelPath)
df = df.where(pd.notnull(df), None)  # Replace NaN with None (optional, good for nulls)
df = df.astype(object)  # This makes each cell a plain Python object instead of numpy dtypes

header = df.head(0)
row_count = df.shape[0]


# class DrawingSet(Base):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.speckle_type = "Collection" 
#         self.collectionType = collection_type

# class DrawingObject(Base):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.speckle_type = "Base" 

#-------------------------------------------------------
# Object creation - Many Children
#-------------------------------------------------------
pt = Point(x=0,y=0,z=0)

dwgs = []
for i in range(5):
    dwg_obj = Base(name="My Drawing")
    dwg_obj["Dossier"] = "0104"
    dwg_obj["Revision"] = "A"
    dwg_obj["@displayValue"] = pt
    dwgs.append(dwg_obj)

drawing_set = Collection(
    name="Drawing Set",
    elements=dwgs
)

# # STEP 2: Create a parent Base object
# parent = Base()

# # STEP 3: Convert each row into a separate Base (child) object
# for i, row_data in df.iterrows():
#     child = Base()
#     # Optionally, give it a custom speckle_type (not strictly required)
#     child.speckle_type = "Base"

#     # Assign row data as properties in the Base object
#     for col_name in df.columns:
#         child[col_name] = row_data[col_name]

#     # ADD A UNIQUE TIMESTAMP
#     child["timestamp"] = datetime.utcnow().isoformat()

#     parent[f"@child_{i}"] = child

#-------------------------------------------------------
# Object creation - Collection
#-------------------------------------------------------

# # STEP 2: Create a parent Base object
# myModel = Base()
# myModel.speckle_type = "Base"

# # 3) Create a sub-collection for "Structural Framing"
# #    In the viewer, this will appear as a group/category.
# drawing_collection = Base()
# drawing_collection.name = "Drawing Collection"    # optional
# # Set a speckle_type so the viewer recognizes it as a container
# drawing_collection.speckle_type = "Collection"

# # 4) Gather dwg objects under this "Drawing Collection" collection
# drawing_objects = []
# # STEP 3: Convert each row into a separate Base (child) object
# for i, row_data in df.iterrows():
#     drawing_object = Base()
#     # Optionally, give it a custom speckle_type (not strictly required)
#     drawing_object.speckle_type = "Base" 

#     # Assign row data as properties in the Base object
#     for col_name in df.columns:
#         drawing_object[col_name] = row_data[col_name]

#     # ADD A UNIQUE TIMESTAMP
#     drawing_object["timestamp"] = datetime.utcnow().isoformat()

#     # parent[f"@child_{i}"] = child
#     drawing_objects.append(drawing_object)

# # 5) Detach the dwgs under drawing_collection. Use a property that starts with '@'.
# drawing_collection["@elements"] = drawing_objects

# # 6) Attach the "drawing_collection" collection to our main "myModel"
# myModel["@DrawingCollection"] = drawing_collection

#-------------------------------------------------------
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
client.branch.create(stream_id, name = model_name, description = "Uploaded drawing objects as a Base object")

transport = ServerTransport(client=client, stream_id=stream_id)

parent_id = send(base=drawing_set, transports=[transport])

commit_id = client.commit.create(
    stream_id=stream_id,
    object_id=parent_id,
    branch_name=model_name,
    message="T12 - Drawing Set with Base named as Dwg"
)
