import os
import subprocess
import tkinter as tk
from queue import Queue, Empty
from threading import Thread

MAX_PROCESSES = 8

class ScriptExecutor:
    def __init__(self, script, logfile):
        self.script = script
        self.logfile = logfile
        self.process = None
        self.closed_naturally = False
        self.closed_error = False


    def execute(self):
        try:
            with open(self.logfile, 'w') as file:
                self.process = subprocess.Popen(['python', self.script], stdout=file, stderr=file)
                self.process.wait()  # Wait for the script to finish
            if self.process.returncode != 0:
                print(f"Script {self.script} encountered an error and closed.")
                self.closed_error = True
            else:
                print(f"{self.script} has finished running")
                self.closed_naturally = True
        except Exception as e:
            print(f"An error occurred while executing script {self.script}: {str(e)}")


def execute_scripts_in_directory(directory):
    # Get the list of scripts in the directory
    scripts = [file for file in os.listdir(directory) if file.endswith('.py')]

    # Create ScriptExecutor instances for each script
    script_executors = []
    for script in scripts:
        logfile = "Logs\\" + os.path.splitext(script)[0] + '.log'
        script_executor = ScriptExecutor(os.path.join(directory, script), logfile)
        script_executors.append(script_executor)

    # Create the GUI
    root = tk.Tk()
    root.title("Active Scripts")

    scripts_frame = tk.Frame(root)
    scripts_frame.pack()

    # Create labels to display active scripts
    script_labels = []
    for i, script_executor in enumerate(script_executors):
        label = tk.Label(scripts_frame, text=script_executor.script)
        label.grid(row=i, column=0, sticky="w")
        script_labels.append(label)

    # Execute scripts using a queue and update the GUI
    def worker():
        while True:
            try:
                script_executor = queue.get(timeout=1)
                script_executor.execute()
                queue.task_done()
            except Empty:
                break

    queue = Queue()

    for script_executor in script_executors:
        queue.put(script_executor)

    for _ in range(min(MAX_PROCESSES, len(script_executors))):
        thread = Thread(target=worker)
        thread.daemon = True
        thread.start()

    # Update the GUI periodically
    def update_scripts_display():
        for i, script_executor in enumerate(script_executors):
            if script_executor.closed_naturally:
                script_labels[i].config(foreground="blue")  # Update color for scripts that closed naturally
            elif script_executor.closed_error:
                script_labels[i].config(foreground="red")
            elif script_executor.process and script_executor.process.poll() is None:
                script_labels[i].config(foreground="green")
            else:
                script_labels[i].config(foreground="black")

        root.after(1000, update_scripts_display)


    update_scripts_display()
    root.mainloop()


if __name__ == "__main__":
    # Example usage
    directory_path = os.getcwd() + "\\Scrapers"  # Replace with your desired directory
    execute_scripts_in_directory(directory_path)
