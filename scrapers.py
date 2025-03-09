import subprocess
import time

# List of scripts to run
scripts = [
    "dankscraper.py",
    "rarescraper.py",
    "fakescraper.py",
    "wojakscraper.py",
    "stampscraper.py",
    "bitcornscraper.py",
    "fakecommonscraper.py",
    "rarecocoscraper.py"
]

# Run each script one by one
for script in scripts:
    try:
        print(f"Starting {script}...")
        # Run the script and wait for it to finish before continuing
        subprocess.run(["python", script], check=True)  # Use "python3" if needed
        print(f"Finished {script}")
        time.sleep(10)  # Optional delay between scripts (adjust as needed)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")