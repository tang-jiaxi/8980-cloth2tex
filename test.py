import torch
from pytorch3d.structures import Meshes
from pytorch3d.renderer import MeshRasterizer, FoVPerspectiveCameras, RasterizationSettings

device = torch.device("cuda:0")

# Dummy mesh: 1000 verts, 2000 faces
verts = torch.rand((1, 1000, 3), device=device)
faces = torch.randint(0, 1000, (1, 2000, 3), device=device)
mesh = Meshes(verts=verts, faces=faces)

# Simple camera + rasterizer
cameras = FoVPerspectiveCameras(device=device)
raster_settings = RasterizationSettings(image_size=256)
rasterizer = MeshRasterizer(cameras=cameras, raster_settings=raster_settings)

# Try GPU rasterization
fragments = rasterizer(mesh)
print("✅ PyTorch3D GPU rasterizer working!")
