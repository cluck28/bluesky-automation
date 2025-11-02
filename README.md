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
pip3 install -r requirements.txt
```

and run 

```bash
cd ./src && python3 app.py
```

## Setting Up Scheduled Posts

After adding posts to be scheduled you need to create a cron job that will check for posts to be sent. Start
by editting your crontab
```bash
crontab -e
```

You need to add this line:
```cron
15 * * * * cd /path/to/project/src && /path/to/project/bluesky/bin/python run_scheduler.py >> /path/to/project/logs/run_scheduler.log 2>&1
```

where you need to replace `/path/to/project` with the path to the project.