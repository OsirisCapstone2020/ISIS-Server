# Flask server that runs ISIS commands

## Environment
Any environment variables without a default are required for the app to start

| Name | Description | Default |
| ---- | ----------- | ------- |
| APP_LOG_LEVEL | A log level name (see [Python docs](https://docs.python.org/3/library/logging.html#logging-levels)) | "info" |
| APP_PORT | The port that the app should run on | 8080 |
| APP_SMTP_SERVER | The SMTP server for emailing pipeline output | |
| APP_SMTP_PORT | The port for APP_SMTP_SERVER | 587 |
| APP_SMTP_USERNAME | The username APP_SMTP_SERVER | |
| APP_SMTP_PASSWORD | The password APP_SMTP_USERNAME | |
| S3_SERVER | The URL of the S3 server that the app should use to store intermediate data | |
| S3_BUCKET | The name of the S3 bucket that the app should use | |
| S3_ACCESS_KEY | The access key for S3_BUCKET | |
| S3_SECRET_KEY | The secret key for S3_BUCKET | |

These variables can be set directly from the CLI or in a .env file at the root
of the app:
```dotenv
APP_LOG_LEVEL=debug
APP_PORT=8080

APP_SMTP_SERVER=...
APP_SMTP_PORT=...
APP_SMTP_USERNAME=...
APP_SMTP_PASSWORD=...

S3_SERVER=...
S3_BUCKET=...
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
```


## Development
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
$ conda env update -p ./.python -f environment.yml --prune
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
