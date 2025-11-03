# Bluesky Project

This project uses a Python virtual environment and relies on a few static directories for uploads and scheduling.

## Setup

To set up the environment and create the required directories and files, simply run:

```bash
make setup
```

The setup steps will do the following:
- create a virtual environment and install the requirements
- add the uploads and schedule folders to handle automating posting with the Bluesky client
- add an .env file -- you will need to put your Bluesky credentials in here
- add a cron job to handle automatic posting

## Running The App

To run the app you just need to activate your virtual environment
```bash
source bluesky/bin/activate
```

and run 

```bash
python ./src/app.py
```

This should result in:
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5555
 * Running on http://192.168.2.25:5555
Press CTRL+C to quit
 * Restarting with stat
```

which you can access on your local host.
