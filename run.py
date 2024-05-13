import subprocess

scripts = ['bdgc1.py', 'bdgc2.py', 'bdgc3.py', 'bdgbot.py']

processes = []
for script in scripts:
    process = subprocess.Popen(['python3', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    processes.append(process)

for process in processes:
    process.wait()

print("All scripts have finished running.")
