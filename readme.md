# Installation as library (any platform):
```
./setup.py install
```

# Build (Mac):
```
make macbundle
```

# Build (Windows):
Make sure to delete `build` and `dist` folders before re-building, as well as `config\login.json` (unless you *want* to give your credentials out).
```
pyinstaller '.\futgui\FIFA 16 Auto Buyer.spec'
```
