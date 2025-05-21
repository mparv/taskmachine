import subprocess
import signal
import sys
import time
import os

new_path = os.path.join(".", "projects", "task-machine", "src", "tm")
new_path2 = os.path.join(".", "projects", "task-machine", "src", "tm", "tm_logging")
os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "") + ";" + new_path + ";" + new_path2

# TODO go build -o universe.exe server.go
# TODO go build -o nice.exe .\main.go

if len(sys.argv) != 4:
    print("Usage: python starter.py <tm.cfg> <universe.cfg> <data_dir>")
    print("tm.cfg is main config file, universe.cfg for db, data_dir for network usage and others")
    sys.exit(1)

tm_cfg = sys.argv[1]
universe_cfg = sys.argv[2]
data_dir = sys.argv[3]

commands = [
    ["python", "tools/network-usage.py", data_dir],
    ["./projects/universal-fomo-db/src/universe-db/universe.exe", universe_cfg],
    ["./projects/task-machine/src/tm/nice/nice.exe", tm_cfg],
    ["python", "projects/task-machine/src/tm/server/app_test.py", tm_cfg, data_dir],
    ["python", "projects/investments/investments_runner.py", tm_cfg]
]

processes = [subprocess.Popen(cmd) for cmd in commands]


def terminate_processes(signal_received, frame):
    print("\nTermination signal received. Stopping all processes...")
    for proc in processes:
        proc.terminate()  # Send termination signal to each process
    for proc in processes:
        proc.wait()  # Wait for each process to finish
    print("All processes stopped.")
    sys.exit(0)

# Register the signal handlers
signal.signal(signal.SIGTERM, terminate_processes)
signal.signal(signal.SIGINT, terminate_processes)




# Keep the main script running so the processes stay alive
print("All processes started. Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    terminate_processes(signal.SIGINT, None)
