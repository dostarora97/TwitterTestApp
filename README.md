# 1. About
Get **Favourited Media** from a Twitter Account

# 2. Installation
## 2.1 Local
```
git clone https://github.com/dostarora97/TwitterTestApp.git
cd TwitterTestApp
python -m pip install -r requirements.txt
python favs_v2.py
```
## 2.2 Colab
Insert this in the cell and run.
```
!git clone https://github.com/dostarora97/TwitterTestApp.git
!mv ./TwitterTestApp/* .
!rm -rf TwitterTestApp
!python -m pip install -r requirements.txt
!python favs_v2.py
import IPython
IPython.display.HTML(filename="data/media.html")
```

## 2.3 Prerequisites
You need to have Twitter Developer account. Apply [here](https://developer.twitter.com/en/apply-for-access)
After making a developer account, get access keys for your [app](https://developer.twitter.com/en/apps)

# 3. Note
All data will be downloaded to `.data` directory.
