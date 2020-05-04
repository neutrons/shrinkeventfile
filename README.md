# shrinkeventfile
This program will crop event files by writing only a specified array 
size to a new file. Much of the code design was ported from NXconvert.
shrinkeventfile makes assumptions based on the structure of files at
SNS and may or may not work for event file from other places.

## Quickstart (w/ Docker)
```
docker build -t myshrink .
docker run -v $(pwd):/data myshrink shrinkeventfile /data/infile.nxs /data/outfile.nxs
```

## Development

Here you can setup a Docker container to work in:
```
docker build -f dockerfiles/Dockerfile.ubuntu_bionic_test_single_python -t myshrink-dev .
docker run -it -v $(pwd):/app-dev myshrink-dev bash
```

NOTE: To "live edit" the application (synced with the host),
        switch to the `/app-dev` directory inside the container

## Run tests

```
docker run  myshrink-dev pytest tests/
```

# Coverage report with lines listed that are NOT yet tested
```
docker run  myshrink-dev pytest --cov-report term-missing  --cov=shrinkeventfile/ tests/test_shrinkeventfile.py
```
