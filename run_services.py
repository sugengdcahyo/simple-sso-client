import subprocess
import os


def run_service_a():
    env = os.environ.copy()
    env["FLASK_APP"] = "app.py"

    process_a = subprocess.Popen(
        ["flask", "run", "--port", "1234"],
        cwd="service_a",
        env=env
    )

    return process_a


def run_service_b():
    env = os.environ.copy()
    env["FLASK_APP"] = "app.py"
    
    process_b = subprocess.Popen(
        ["flask", "run", "--port", "1235"],
        cwd="service_b",
        env=env
    )


if __name__ == "__main__":
    process_a = run_service_a()
    process_b = run_service_b()

    try:
        process_a.wait()
        process_b.wait()
    except KeyboardInterrupt:
        process_a.terminate()
        process_b.terminate()
