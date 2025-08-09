#!/usr/bin/env python3
"""
Smart Server Management Script
Prevents multiple server instances and ensures clean startup
"""

import subprocess
import sys
import time
import os
import signal
from typing import List, Tuple

def get_processes_on_port(port: int = 8000) -> List[Tuple[str, str]]:
    """Get all processes running on the specified port"""
    try:
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        processes = []
        for line in result.stdout.strip().split('\n'):
            if line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    processes.append((line.strip(), pid))
        
        return processes
    except Exception as e:
        print(f"Error checking port {port}: {e}")
        return []

def kill_processes_on_port(port: int = 8000) -> bool:
    """Kill all processes running on the specified port"""
    processes = get_processes_on_port(port)
    
    if not processes:
        print(f"✅ No processes found on port {port}")
        return True
    
    print(f"🔍 Found {len(processes)} processes on port {port}:")
    pids_to_kill = []
    
    for process_info, pid in processes:
        print(f"  - PID {pid}: {process_info}")
        pids_to_kill.append(pid)
    
    if pids_to_kill:
        print(f"🔪 Killing {len(pids_to_kill)} processes...")
        try:
            # Kill all PIDs at once
            pids_str = ' '.join([f'/PID {pid}' for pid in pids_to_kill])
            result = subprocess.run(
                f'taskkill {pids_str} /F',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ All processes killed successfully")
                time.sleep(2)  # Wait for processes to fully terminate
                return True
            else:
                print(f"❌ Error killing processes: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error killing processes: {e}")
            return False
    
    return True

def start_server(port: int = 8000, host: str = "127.0.0.1") -> bool:
    """Start the FastAPI server with proper checks"""
    try:
        print(f"🚀 Starting server on {host}:{port}...")
        
        # Start the server
        cmd = f"python -m uvicorn main:app --reload --host {host} --port {port}"
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=os.getcwd()
        )
        
        # Wait a moment and check if it started successfully
        time.sleep(3)
        
        # Check if the process is still running
        if process.poll() is None:
            print(f"✅ Server started successfully on http://{host}:{port}")
            print(f"📊 Server PID: {process.pid}")
            print("🔄 Server is running with auto-reload enabled")
            print("⏹️  Press Ctrl+C to stop the server")
            
            try:
                # Keep the script running and monitor the server
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
                process.terminate()
                time.sleep(2)
                if process.poll() is None:
                    process.kill()
                print("✅ Server stopped")
            
            return True
        else:
            print(f"❌ Server failed to start (exit code: {process.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def main():
    """Main server management function"""
    print("🔧 eBay Auto Parts Lister - Smart Server Manager")
    print("=" * 50)
    
    port = 8000
    host = "127.0.0.1"
    
    # Step 1: Check for existing processes
    print(f"🔍 Checking for existing processes on port {port}...")
    existing_processes = get_processes_on_port(port)
    
    if existing_processes:
        print(f"⚠️  Found {len(existing_processes)} existing processes on port {port}")
        
        # Ask user what to do
        while True:
            choice = input("Do you want to kill existing processes and start fresh? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                if not kill_processes_on_port(port):
                    print("❌ Failed to kill existing processes. Exiting.")
                    sys.exit(1)
                break
            elif choice in ['n', 'no']:
                print("❌ Cannot start server with existing processes running. Exiting.")
                sys.exit(1)
            else:
                print("Please enter 'y' or 'n'")
    
    # Step 2: Verify port is clear
    final_check = get_processes_on_port(port)
    if final_check:
        print(f"❌ Port {port} is still occupied after cleanup. Exiting.")
        sys.exit(1)
    
    # Step 3: Start the server
    success = start_server(port, host)
    
    if not success:
        print("❌ Failed to start server")
        sys.exit(1)

if __name__ == "__main__":
    main()
