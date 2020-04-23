# shrinkeventfile
This program will crop event files by writing only a specified array 
size to a new file. Much of the code design was ported from NXconvert.
shrinkeventfile makes assumptions based on the structure of files at
SNS and may or may not work for event file from other places.

## Development

Here you can setup a Docker container to work in:
```
docker build --build-arg VIMRC="$(cat $HOME/.vimrc)" -t myshrink .
docker run -it -v $(pwd):/app-dev myshrink bash
```

NOTE: To "live edit" the application (synced with the host),
        switch to the `/app-dev` directory inside the container

# Run tests
```
pytest tests/
```

# Coverage report with lines listed that are NOT yet tested
```
pytest  --cov-report term-missing  --cov=shrinkeventfile/ tests/test_shrinkeventfile.py
```
