# Set-up and Environment
* WSL2 Ubuntu x86_64
* Python 3.8
## 1. Set up virtual environment
Install packages to be contained in this environment
```
python3.8 -m venv .venv
source .venv/bin/activate
```
## 2. Download external packages
[Nvida cudaTools 11.7.0](https://developer.nvidia.com/cuda-11-7-0-download-archive)  
Linux x86_64 WSL-Ubuntu 2.0 deb(local)  
[Nvidia cuDNN 9.8.0](https://developer.nvidia.com/cudnn-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=20.04&target_type=deb_local)  
Linux x86_64 Ubuntu 20.04 deb(local)  
_deb lets you download from terminal_

## 3. Download packages
Adapted from [Cloth2Tex repo](https://github.com/HumanAIGC/Cloth2Tex)
```
sudo apt-get update -y
sudo apt-get install libgl1
sudo apt-get install libboost-dev
```
wheels take a lot longer to download
```
pip install -r requirements.txt #you're welcome for this crying 
pip install torch_geometric
pip install pyg_lib-0.3.0+pt113cu117-cp38-cp38-linux_x86_64.whl
pip install torch_cluster-1.6.1+pt113cu117-cp38-cp38-linux_x86_64.whl
pip install torch_scatter-2.1.1+pt113cu117-cp38-cp38-linux_x86_64.whl
pip install torch_sparse-0.6.15+pt113cu117-cp38-cp38-linux_x86_64.whl
```
## 4. Clone repos 
The shorter installation instructions didn't work for me so I cloned the repos locally but you can try those first
### pytorch3D 
* Very important!! Must have these versions (is in requirement.txt already) before installing
  * `torch==1.13.1+cu117`
  * `torchaudio==0.13.1+cu117`
  * `torchvision==0.14.1+cu117` <br>
^cu117 is for nvida drivers, need to download something else if not cuda but idk if it will work
```
#for simplicity just clone it in the same directory
git clone https://github.com/facebookresearch/pytorch3d.git
cd pytorch3d
FORCE_CUDA=1 pip install .  #must force CUDA so it installs the GPU version of pytorch3d
```
Verify installation
```
python -c "from pytorch3d.structures import Meshes"
#shouldnt print anything
```
### psbody-mesh
```
git clone https://github.com/MPI-IS/mesh.git
pip install . 
```
Verify installation
```
python -c "from psbody.mesh import Mesh"
#shouldnt print anything
```
## Verify package installation
```
pip list
#prints all your packages, including those cloned from repos
pip show [package-name]
#prints additional info about a specific package
```
If there are any packages you need but aren't installed, will probably show up in 'Problems' tab in VSCode's terminal ribbon

# How to use 
## Starting the server
Listens on localhost:port=5000
```
python3 server.py
```
Customizable command flags in `server.py` 
* `--s`: scale of mesh
* `--steps_one`: higher number = more detailed shape
* `--steps_two`: higher number = more detailed texture
## 1. Sending a request from Unity
1. Click UploadDesign game object and populate input fields
2. Click 'Generate Texture' button OR right-click `Cloth Texture Uploader` script header for context menu > `Upload and Apply Texture` to send
3. On success, Unity receives the `session_id` back and stores it in PlayerPreferences.
4. While in play mode, Unity polls `/status/<session_id>` for the generated texture 
## 2. Server receives the request and runs it through the model to send back a texture
1. Server immediately sends back the generated `session_id` to Unity (^step 1.3)
2. Server runs the model in the background and updates `/status/<session_id>` endpoint when it's done
* Raw files uploaded from Unity are stored in `/uploads/<session_id>` folder
* Results are stored in `experiments/[session_time]` folder
* Step1 in the training process will be skipped if the mesh has been cached before
## 3. Receiving the texture back in Unity
1. When Unity receives the success status, it accesses the `/results/<session_id>` to download the texture file
2. Unity applies the texture to all materials in its mesh
3. On success, Unity deletes the stored `session_id` key in PlayerPreferences

# Potential Bugs
## Cannot open shared object file
* Run `nano ~/.bashrc`
* Add this line `export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH` to your bash file
* Run `source ~/.bashrc`
## Cannot find libcuda.so 
Verify libcuda.so installation
```
ldconfig -p | grep libcuda
#should print a bunch of symlinks related to libcuda 
python -c "from ctypes.util import find_library; print(find_library('cuda'))"
#should print libcuda.so[.X]
```
If X exists or you have a hard link, it's probably a missing sym link issue
```
sudo rm /usr/lib/wsl/lib/libcuda.so #remove the current file
sudo ln -s /usr/lib/wsl/lib/libcuda.so.1 /usr/lib/wsl/lib/libcuda.so #create a new symlink
```
Verify that your libcuda.so is now discoverable
```
python -c "import ctypes; ctypes.CDLL('libcuda.so')"
#should print cuda file path or file name
ls -l /usr/lib/wsl/lib/libcuda.so
#should print symlink libcuda.so -> libcuda.so.[X]
python -c "import ctypes; ctypes.CDLL('libcuda.so')"
#if nothing is printed, means this file is sucessfully linked and usable
```
## Some cloned library is editable
Don't use `-e` flag when installing with `pip`, try `pip install .` or `pip install --no-editable flag`
  
# Debugging
## Can my PyTorch see my GPU?
```
python -c "import torch; print(torch.cuda.is_available())"
#should print True
python -c "import torch; print(torch.cuda.device_count()); print(torch.cuda.get_device_name(0))"
#should print your GPU name 
```
## Verify Nvida driver installation
Shouldn't need to install Nvida drivers inside WSL (cudaTool handles it), only install it in Windows if needed
```
nvidia-smi
#should print your driver info in both Windows and WSL if they are installed properly
```
