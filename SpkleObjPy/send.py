import os 
from datetime import datetime

from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.objects import Base

from specklepy.objects.geometry import Mesh

from specklepy.transports.server import ServerTransport
from specklepy.api.operations import send

import pandas as pd 

class MyObject(Base):
    title: str
    _building: str  # We'll store the actual building value here

    def __init__(self, title="Untitled", building="Unknown", **kwargs):
        super().__init__(**kwargs)
        self._title = title
        self._building = building

    @property
    def building(self):
        return self._building

    @building.setter
    def building(self, value: str):
        self._building = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value


def create_triangle_mesh() -> Mesh:
    mesh = Mesh()
    
    # A mesh’s vertices must be a *flat list* of x,y,z coordinates in object space
    # For example, here's a triangle with 3 vertices and 1 triangular face:
    mesh.vertices = [
        0, 0, 0,   # vertex 0
        1, 0, 0,   # vertex 1
        0, 1, 0    # vertex 2
    ]
    
    # The faces array describes how vertices form triangles or quads in Speckle:
    # The first number is the number of vertices in the face + an offset (either 0 or 1).
    # For a single triangle face with 3 corners, we use '3' plus the offset '2', so 3+2=5
    # Then the indices of the 3 vertices
    mesh.faces = [
        5, 0, 1, 2
    ]
    
    # The units property is recommended
    mesh.units = "m"
    
    return mesh

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

#-------------------------------------------------------
# Object creation - Many Children
#-------------------------------------------------------

triangle = create_triangle_mesh()


dwg_obj = MyObject(title="Haute", building="SP" )

dwg_obj["Dossier"] = "0104"
dwg_obj["@Revision"] = "A"

# The KEY: attach geometry so the viewer can display it
dwg_obj["displayValue"] = triangle

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

parent_id = send(base=dwg_obj, transports=[transport])

commit_id = client.commit.create(
    stream_id=stream_id,
    object_id=parent_id,
    branch_name=model_name,
    message="T8"
)
