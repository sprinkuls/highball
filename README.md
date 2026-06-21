# highball

## installation

Ingredients:

- Python (probably some Python 3 will work fine) (i'm using 3.13)

linux:

``` bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
curl -o static/htmx.min.js https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js
```

windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\requirements.txt
curl -o static/htmx.min.js https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js
```