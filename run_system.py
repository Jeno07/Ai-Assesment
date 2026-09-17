import os
import sys
import subprocess
import time

def run():
    print("=" * 70)
    print("🚀 Starting AI Customer Support Ticket System...")
    print("=" * 70)
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    server_dir = os.path.join(root_dir, "server")
    client_dir = os.path.join(root_dir, "client")
    
    # 1. Check & Initialise DB
    print("\n[1/3] Initializing Database & CSV Dataset...")
    sys.path.insert(0, root_dir)
    try:
        from server.db import init_db
        init_db()
    except Exception as e:
        print(f"[Warning] DB initialization step: {e}")
        
    # 2. Launch FastAPI Server
    print("\n[2/3] Launching FastAPI Backend on http://localhost:8000 ...")
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=root_dir
    )
    
    time.sleep(2)
    
    # 3. Launch React Client
    print("\n[3/3] Launching React Client UI on http://localhost:3000 ...")
    client_proc = subprocess.Popen(
        ["npx.cmd", "vite"],
        cwd=client_dir,
        shell=True
    )
    
    print("\n" + "=" * 70)
    print("✅ System successfully started!")
    print(" - Backend API Documentation: http://localhost:8000/docs")
    print(" - Frontend Dashboard:         http://localhost:3000")
    print("=" * 70 + "\n")
    
    try:
        server_proc.wait()
        client_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
        server_proc.terminate()
        client_proc.terminate()

if __name__ == "__main__":
    run()
