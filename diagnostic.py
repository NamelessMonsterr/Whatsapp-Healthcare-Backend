#!/usr/bin/env python3
"""
WhatsApp Bot Full Diagnostic Script
Checks all components of your WhatsApp sandbox chatbot setup
"""

import os
import sys
import json
import time
import requests
import subprocess
import socket
from datetime import datetime
from pathlib import Path
import urllib.parse
from typing import Dict, List, Tuple
import platform

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")

def print_status(label, status, details=""):
    if status:
        symbol = "✅"
        color = Colors.GREEN
    else:
        symbol = "❌"
        color = Colors.FAIL
    
    print(f"{color}{symbol} {label}{Colors.ENDC}")
    if details:
        print(f"   {Colors.CYAN}→ {details}{Colors.ENDC}")

def print_info(label, value):
    print(f"{Colors.BLUE}ℹ️  {label}:{Colors.ENDC} {value}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

class WhatsAppBotDiagnostic:
    def __init__(self):
        self.results = {}
        self.fastapi_url = "http://localhost:8000"
        self.ngrok_api = "http://localhost:4040/api"
        self.errors = []
        self.warnings = []
        
    def run_full_diagnostic(self):
        """Run complete diagnostic suite"""
        print(f"{Colors.BOLD}{Colors.CYAN}")
        print("🔍 WHATSAPP BOT DIAGNOSTIC TOOL")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Colors.ENDC}")
        
        # System Information
        self.check_system_info()
        
        # Python Environment
        self.check_python_environment()
        
        # Network and Ports
        self.check_network()
        
        # FastAPI Server
        self.check_fastapi_server()
        
        # Ngrok Tunnel
        self.check_ngrok()
        
        # File System and Logs
        self.check_filesystem()
        
        # Dependencies
        self.check_dependencies()
        
        # Test Endpoints
        self.test_endpoints()
        
        # Check Running Processes
        self.check_processes()
        
        # Twilio Configuration (if credentials available)
        self.check_twilio_config()
        
        # Generate Report
        self.generate_report()
        
    def check_system_info(self):
        """Check system information"""
        print_header("SYSTEM INFORMATION")
        
        print_info("Operating System", platform.system())
        print_info("OS Version", platform.version())
        print_info("Python Version", sys.version)
        print_info("Platform", platform.platform())
        print_info("Processor", platform.processor())
        print_info("Current Directory", os.getcwd())
        print_info("User", os.environ.get('USER', 'Unknown'))
        
    def check_python_environment(self):
        """Check Python environment and virtual env"""
        print_header("PYTHON ENVIRONMENT")
        
        # Check if in virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        print_status("Virtual Environment Active", in_venv)
        if in_venv:
            print_info("Virtual Env Path", sys.prefix)
        
        # Check Python path
        print_info("Python Executable", sys.executable)
        print_info("Python Path", "\n   ".join(sys.path[:3]))
        
    def check_network(self):
        """Check network connectivity and ports"""
        print_header("NETWORK DIAGNOSTICS")
        
        # Check localhost
        try:
            socket.gethostbyname('localhost')
            print_status("Localhost Resolution", True)
        except:
            print_status("Localhost Resolution", False)
            self.errors.append("Cannot resolve localhost")
        
        # Check specific ports
        ports_to_check = [
            (8000, "FastAPI Server"),
            (4040, "Ngrok Web Interface"),
            (80, "HTTP"),
            (443, "HTTPS")
        ]
        
        for port, service in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            is_open = result == 0
            print_status(f"Port {port} ({service})", is_open)
            
            if port == 8000 and not is_open:
                self.errors.append("FastAPI server port 8000 is not open")
        
        # Check internet connectivity
        try:
            requests.get("https://www.google.com", timeout=5)
            print_status("Internet Connectivity", True)
        except:
            print_status("Internet Connectivity", False)
            self.warnings.append("No internet connection detected")
            
    def check_fastapi_server(self):
        """Check if FastAPI server is running"""
        print_header("FASTAPI SERVER STATUS")
        
        endpoints_to_test = [
            ("/", "Root Endpoint"),
            ("/health", "Health Check"),
            ("/docs", "API Documentation"),
            ("/webhook", "Webhook Endpoint (GET)"),
        ]
        
        for endpoint, description in endpoints_to_test:
            try:
                response = requests.get(f"{self.fastapi_url}{endpoint}", timeout=5)
                success = response.status_code in [200, 405, 422]
                print_status(
                    f"{description} - {endpoint}", 
                    success,
                    f"Status Code: {response.status_code}"
                )
                
                if endpoint == "/" and success:
                    try:
                        data = response.json()
                        print_info("Server Response", data)
                    except:
                        pass
                        
            except requests.ConnectionError:
                print_status(f"{description} - {endpoint}", False, "Connection Failed")
                self.errors.append(f"Cannot connect to FastAPI endpoint {endpoint}")
            except Exception as e:
                print_status(f"{description} - {endpoint}", False, str(e))
                
    def check_ngrok(self):
        """Check ngrok tunnel status"""
        print_header("NGROK TUNNEL STATUS")
        
        try:
            # Check ngrok API
            response = requests.get(f"{self.ngrok_api}/tunnels", timeout=5)
            
            if response.status_code == 200:
                tunnels = response.json().get('tunnels', [])
                
                if tunnels:
                    print_status("Ngrok Running", True, f"Found {len(tunnels)} tunnel(s)")
                    
                    for tunnel in tunnels:
                        print(f"\n{Colors.CYAN}📡 Tunnel Details:{Colors.ENDC}")
                        print_info("  Name", tunnel.get('name'))
                        print_info("  Public URL", tunnel.get('public_url'))
                        print_info("  Protocol", tunnel.get('proto'))
                        print_info("  Local Address", tunnel.get('config', {}).get('addr'))
                        
                        # Store public URL for later tests
                        if tunnel.get('proto') == 'https':
                            self.results['ngrok_url'] = tunnel.get('public_url')
                else:
                    print_status("Ngrok Running", False, "No active tunnels found")
                    self.errors.append("Ngrok is running but no tunnels are active")
                    
            else:
                print_status("Ngrok API", False, f"Status Code: {response.status_code}")
                
        except requests.ConnectionError:
            print_status("Ngrok", False, "Not running or API not accessible")
            self.errors.append("Ngrok is not running. Start it with: ngrok http 8000")
            
            # Try to start ngrok
            print_warning("Attempting to check if ngrok is installed...")
            try:
                result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
                print_info("Ngrok Version", result.stdout.strip())
            except FileNotFoundError:
                print_error("Ngrok is not installed. Install from: https://ngrok.com/download")
                
    def check_filesystem(self):
        """Check file system and log files"""
        print_header("FILE SYSTEM & LOGS")
        
        # Check current directory permissions
        current_dir = Path.cwd()
        can_write = os.access(current_dir, os.W_OK)
        print_status("Write Permission (Current Dir)", can_write)
        
        if not can_write:
            self.errors.append("Cannot write to current directory")
        
        # Check for log files
        log_files = [
            "whatsapp_bot.log",
            "messages_log.json",
            "bot.log",
            "error.log"
        ]
        
        print(f"\n{Colors.CYAN}📄 Log Files:{Colors.ENDC}")
        for log_file in log_files:
            path = Path(log_file)
            if path.exists():
                size = path.stat().st_size
                modified = datetime.fromtimestamp(path.stat().st_mtime)
                print_status(
                    log_file, 
                    True, 
                    f"Size: {size} bytes, Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                # Check if file is growing (recent activity)
                if (datetime.now() - modified).seconds > 3600:
                    print_warning(f"  {log_file} hasn't been updated in over an hour")
                    
                # Read last few lines
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"  {Colors.CYAN}Last log entry:{Colors.ENDC}")
                            print(f"    {lines[-1].strip()[:100]}")
                except Exception as e:
                    print_warning(f"  Cannot read {log_file}: {e}")
            else:
                print_status(log_file, False, "File not found")
                
        # Create test log file
        print(f"\n{Colors.CYAN}Testing file write capability...{Colors.ENDC}")
        test_file = "diagnostic_test.log"
        try:
            with open(test_file, 'w') as f:
                f.write(f"Diagnostic test at {datetime.now()}\n")
            print_status("Test File Creation", True, test_file)
            os.remove(test_file)
        except Exception as e:
            print_status("Test File Creation", False, str(e))
            self.errors.append(f"Cannot create files: {e}")
            
    def check_dependencies(self):
        """Check Python package dependencies"""
        print_header("PYTHON DEPENDENCIES")
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "python-multipart",
            "requests",
            "twilio",  # If using Twilio
            "pydantic",
            "python-dotenv"
        ]
        
        import importlib
        import pkg_resources
        
        for package in required_packages:
            try:
                # Try to import the package
                if package == "uvicorn":
                    importlib.import_module("uvicorn")
                elif package == "python-multipart":
                    importlib.import_module("multipart")
                elif package == "python-dotenv":
                    importlib.import_module("dotenv")
                else:
                    importlib.import_module(package)
                
                # Get version
                try:
                    version = pkg_resources.get_distribution(package).version
                    print_status(package, True, f"Version: {version}")
                except:
                    print_status(package, True, "Version unknown")
                    
            except ImportError:
                print_status(package, False, "Not installed")
                self.warnings.append(f"Missing package: {package}")
                
        # Check for .env file
        print(f"\n{Colors.CYAN}Environment Configuration:{Colors.ENDC}")
        env_file = Path(".env")
        if env_file.exists():
            print_status(".env file", True)
            # Check for common variables (without showing values)
            with open(".env", 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if '=' in line and not line.startswith('#'):
                        key = line.split('=')[0].strip()
                        print_info(f"  Environment Variable", key)
        else:
            print_status(".env file", False, "Not found")
            
    def test_endpoints(self):
        """Test webhook endpoints with sample data"""
        print_header("ENDPOINT TESTING")
        
        if not self.is_server_running():
            print_warning("Skipping endpoint tests - server not running")
            return
            
        # Test webhook with sample Twilio data
        print(f"\n{Colors.CYAN}Testing Webhook with Sample Data:{Colors.ENDC}")
        
        test_data = {
            "Body": "Diagnostic test message",
            "From": "whatsapp:+1234567890",
            "ProfileName": "Diagnostic Tool",
            "MessageSid": "TEST123456789"
        }
        
        try:
            response = requests.post(
                f"{self.fastapi_url}/webhook",
                data=test_data,
                timeout=10
            )
            
            print_status(
                "Webhook POST Test", 
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
            
            if response.status_code == 200:
                print_info("Response Content Type", response.headers.get('content-type'))
                print(f"{Colors.CYAN}Response Body:{Colors.ENDC}")
                print(response.text[:500])
                
                # Check if response is valid TwiML
                if '<?xml' in response.text and '<Response>' in response.text:
                    print_status("Valid TwiML Response", True)
                else:
                    print_status("Valid TwiML Response", False)
                    self.warnings.append("Webhook response is not valid TwiML")
                    
        except Exception as e:
            print_status("Webhook POST Test", False, str(e))
            self.errors.append(f"Webhook test failed: {e}")
            
    def check_processes(self):
        """Check for running Python/FastAPI processes"""
        print_header("RUNNING PROCESSES")
        
        try:
            # Check for Python processes
            result = subprocess.run(
                ['ps', 'aux'], 
                capture_output=True, 
                text=True
            )
            
            processes = result.stdout.split('\n')
            python_processes = []
            ngrok_processes = []
            
            for process in processes:
                if 'python' in process.lower() and ('fastapi' in process.lower() or 'uvicorn' in process.lower() or 'bot' in process.lower()):
                    python_processes.append(process)
                elif 'ngrok' in process.lower():
                    ngrok_processes.append(process)
                    
            if python_processes:
                print_status("FastAPI/Bot Process", True, f"Found {len(python_processes)} process(es)")
                for proc in python_processes[:2]:  # Show first 2
                    # Extract key info
                    parts = proc.split()
                    if len(parts) > 10:
                        pid = parts[1]
                        cpu = parts[2]
                        mem = parts[3]
                        cmd = ' '.join(parts[10:])[:80]
                        print(f"  {Colors.CYAN}PID:{Colors.ENDC} {pid} | {Colors.CYAN}CPU:{Colors.ENDC} {cpu}% | {Colors.CYAN}MEM:{Colors.ENDC} {mem}% | {Colors.CYAN}CMD:{Colors.ENDC} {cmd}...")
            else:
                print_status("FastAPI/Bot Process", False, "No processes found")
                self.errors.append("No FastAPI/bot processes running")
                
            if ngrok_processes:
                print_status("Ngrok Process", True, f"Found {len(ngrok_processes)} process(es)")
            else:
                print_status("Ngrok Process", False, "Not found")
                
        except Exception as e:
            print_warning(f"Cannot check processes: {e}")
            
            # Try alternative method for Windows
            if platform.system() == "Windows":
                try:
                    result = subprocess.run(
                        ['tasklist'], 
                        capture_output=True, 
                        text=True
                    )
                    if 'python' in result.stdout.lower():
                        print_info("Python processes detected (Windows)")
                except:
                    pass
                    
    def check_twilio_config(self):
        """Check Twilio configuration if credentials are available"""
        print_header("TWILIO CONFIGURATION")
        
        # Check for Twilio environment variables
        twilio_vars = {
            "TWILIO_ACCOUNT_SID": os.environ.get("TWILIO_ACCOUNT_SID"),
            "TWILIO_AUTH_TOKEN": os.environ.get("TWILIO_AUTH_TOKEN"),
            "TWILIO_PHONE_NUMBER": os.environ.get("TWILIO_PHONE_NUMBER")
        }
        
        has_credentials = False
        for var_name, var_value in twilio_vars.items():
            if var_value:
                # Show only partial value for security
                masked_value = var_value[:4] + "..." + var_value[-4:] if len(var_value) > 8 else "***"
                print_status(var_name, True, f"Set ({masked_value})")
                has_credentials = True
            else:
                print_status(var_name, False, "Not set")
                
        if has_credentials:
            print_info("Twilio Credentials", "Found (partially shown for security)")
            
            # Try to verify with Twilio API
            try:
                from twilio.rest import Client
                client = Client(twilio_vars["TWILIO_ACCOUNT_SID"], twilio_vars["TWILIO_AUTH_TOKEN"])
                account = client.api.accounts(twilio_vars["TWILIO_ACCOUNT_SID"]).fetch()
                print_status("Twilio Account Valid", True, f"Status: {account.status}")
            except ImportError:
                print_warning("Twilio library not installed - cannot verify credentials")
            except Exception as e:
                print_status("Twilio Account Valid", False, str(e))
                self.warnings.append("Twilio credentials may be invalid")
        else:
            print_warning("No Twilio credentials found in environment")
            
    def is_server_running(self):
        """Check if FastAPI server is running"""
        try:
            response = requests.get(f"{self.fastapi_url}/", timeout=2)
            return response.status_code == 200
        except:
            return False
            
    def generate_report(self):
        """Generate final diagnostic report"""
        print_header("DIAGNOSTIC SUMMARY")
        
        # Count issues
        total_errors = len(self.errors)
        total_warnings = len(self.warnings)
        
        if total_errors == 0 and total_warnings == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ All checks passed! Your bot setup looks good.{Colors.ENDC}")
        else:
            if total_errors > 0:
                print(f"{Colors.FAIL}{Colors.BOLD}❌ Found {total_errors} error(s):{Colors.ENDC}")
                for i, error in enumerate(self.errors, 1):
                    print(f"   {i}. {error}")
                    
            if total_warnings > 0:
                print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  Found {total_warnings} warning(s):{Colors.ENDC}")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"   {i}. {warning}")
                    
        # Provide recommendations
        print_header("RECOMMENDATIONS")
        
        if not self.is_server_running():
            print(f"{Colors.CYAN}1. Start your FastAPI server:{Colors.ENDC}")
            print("   python your_bot.py")
            print("   OR")
            print("   uvicorn main:app --reload --port 8000")
            
        if 'ngrok_url' not in self.results:
            print(f"\n{Colors.CYAN}2. Start ngrok tunnel:{Colors.ENDC}")
            print("   ngrok http 8000")
            
        if self.warnings:
            print(f"\n{Colors.CYAN}3. Install missing dependencies:{Colors.ENDC}")
            print("   pip install fastapi uvicorn python-multipart twilio python-dotenv")
            
        if total_errors == 0 and total_warnings == 0:
            print(f"{Colors.GREEN}Your bot is properly configured!{Colors.ENDC}")
            print(f"\n{Colors.CYAN}Next steps:{Colors.ENDC}")
            print("1. Ensure your Twilio webhook is configured with your ngrok URL")
            print("2. Send a test message from WhatsApp")
            print("3. Monitor logs with: tail -f whatsapp_bot.log")
            
        # Save report to file
        self.save_report()
        
    def save_report(self):
        """Save diagnostic report to file"""
        report_file = f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(report_file, 'w') as f:
                f.write("WHATSAPP BOT DIAGNOSTIC REPORT\n")
                f.write(f"Generated: {datetime.now()}\n")
                f.write("="*60 + "\n\n")
                
                f.write("ERRORS:\n")
                for error in self.errors:
                    f.write(f"  - {error}\n")
                    
                f.write("\nWARNINGS:\n")
                for warning in self.warnings:
                    f.write(f"  - {warning}\n")
                    
                f.write("\nSYSTEM INFO:\n")
                f.write(f"  OS: {platform.system()} {platform.version()}\n")
                f.write(f"  Python: {sys.version}\n")
                f.write(f"  Current Dir: {os.getcwd()}\n")
                
            print(f"\n{Colors.GREEN}📄 Report saved to: {report_file}{Colors.ENDC}")
        except Exception as e:
            print_warning(f"Could not save report: {e}")

def main():
    """Main diagnostic function"""
    try:
        diagnostic = WhatsAppBotDiagnostic()
        diagnostic.run_full_diagnostic()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Diagnostic interrupted by user{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Diagnostic failed with error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()