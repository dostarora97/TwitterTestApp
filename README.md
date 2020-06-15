# TwitterTestApp
To fetch media from liked/favourited tweets.

You need to have Twitter Developer account. Apply here: https://developer.twitter.com/en/apply-for-access.
After making a developer account, get access keys from : https://developer.twitter.com/en/apps

```
git clone https://github.com/dostarora97/TwitterTestApp.git
python -m pip install -r requirements.txt
python favs_v2.py
```
Follow onscreen instructions :
1.  Provide Authentication to the App.
2.  Provide screen_name.  

All data will be downloaded to `.data` directory.  

To run on Google Collab: Insert this in the cell and run.
```
!git clone https://github.com/dostarora97/TwitterTestApp.git
!mv ./TwitterTestApp/* .
!rm -rf TwitterTestApp
!python -m pip install -r requirements.txt
!python favs_v2.py
import IPython
IPython.display.HTML(filename="data/media.html")
```