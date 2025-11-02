# Bluesky Project

This project uses a Python virtual environment and relies on a few static directories for uploads and scheduling.

## Setup

To set up the environment and create the required directories and files, simply run:

```bash
make setup
```

You will also need to add an `.env` file with your Bluesky credentials.

## Running The App

To run the app you just need to activate your virtual environment
```bash
source bluesky/bin/activate
```

and run 

```bash
python3 ./src/app.py
```
