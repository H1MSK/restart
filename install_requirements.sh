# Dependency for Box2d-py
sudo apt install swig -y

conda create -y -n restart python=3.11
conda activate restart

pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
