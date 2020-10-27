# Flask server that runs ISIS commands

1. Install [miniconda3](https://docs.conda.io/en/latest/miniconda.html)
2. Install the project's dependencies into [.python](./.python)
   ```console
   $ conda env create -p .python -f environment.yml
   ```
3. Activate the new environment in .python
   ```console
   $ conda activate ./.python 
   ```
4. Install the development dependencies
    ```console
    $ pip install -r requirements.dev.txt
    ```
4. Start the server, it'll automatically pick up any changes to the code
and restart itself and run on port 8000 by default.
   ```console
   $ gunicorn -c gunicorn.conf.py --reload isis_server:app
   ```

If you make updates to [environment.yml](./environment.yml), you can update
the .python directory to match by running:
```console
$ conda env update -p .python -f environment.yml --prune
$ pip install -r requirements.dev.txt
```

To run tests:
```console
$ pytest
```

To test a command (I00831002RDR.cub available via LFS in [data](./data/test)):
```console
$ curl -s -X POST \
    -H 'Content-Type: application/json' \
    -d '{"cmd": "lowpass", "input_file": "I00831002RDR.cub", "args": []}' \
    localhost:8000 | jq
{
  "output": "I00831002RDR.lowpass.cub"
}
```
