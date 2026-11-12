import subprocess
import sys
import time

def main():
    # Inicia o backend (FastAPI/Uvicorn)
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server_backend:app", "--reload", "--port", "8000"]
    )
    
    # Pequena pausa para garantir que a API suba antes da interface
    time.sleep(2)
    
    # Inicia o frontend (Streamlit)
    frontend = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app_frontend.py"]
    )

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\nEncerrando servidores...")
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()

if __name__ == "__main__":
    main()