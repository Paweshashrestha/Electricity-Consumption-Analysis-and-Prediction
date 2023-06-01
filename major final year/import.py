import multiprocessing
import subprocess

def run_flask_app1():
    subprocess.run(["/usr/local/bin/python3", "./backend/SJNX.py"])

def run_flask_app2():
    subprocess.run(["/usr/local/bin/python3", "./backend/temperature.py"])


def run_streamlit_app():
    subprocess.run(["/usr/local/bin/python3", "-m", "streamlit", "run", "./frontend/main.py"])

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=run_flask_app1)
    p2 = multiprocessing.Process(target=run_flask_app2)
    p3 = multiprocessing.Process(target=run_streamlit_app)

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()