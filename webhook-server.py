#!/usr/bin/env python3
"""
Simple webhook server for auto-deployment
Listens for GitHub webhooks and triggers auto-deployment
"""

import json
import subprocess
import hashlib
import hmac
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

# Configuration
WEBHOOK_PORT = 9000
WEBHOOK_SECRET = "your-webhook-secret-here"  # Change this!
DEPLOY_SCRIPT = "/opt/ebay-auto-parts-lister/auto-deploy.sh"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/webhook-server.log'),
        logging.StreamHandler()
    ]
)

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/webhook':
            self.send_response(404)
            self.end_headers()
            return
        
        # Get content length
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_response(400)
            self.end_headers()
            return
        
        # Read the payload
        payload = self.rfile.read(content_length)
        
        # Verify signature if secret is set
        if WEBHOOK_SECRET and WEBHOOK_SECRET != "your-webhook-secret-here":
            signature = self.headers.get('X-Hub-Signature-256')
            if not signature:
                logging.warning("No signature provided")
                self.send_response(401)
                self.end_headers()
                return
            
            # Verify the signature
            expected_signature = 'sha256=' + hmac.new(
                WEBHOOK_SECRET.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                logging.warning("Invalid signature")
                self.send_response(401)
                self.end_headers()
                return
        
        try:
            # Parse the payload
            data = json.loads(payload.decode('utf-8'))
            
            # Check if this is a push to main branch
            event = data.get('event')
            ref = data.get('ref')
            if event == 'push' and ref == 'refs/heads/main':
                logging.info("Push to main branch detected - triggering auto-deployment")
                
                # Send immediate response to GitHub so git push doesn't hang
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "accepted", "message": "Deployment started"}).encode())
                
                # Run auto-deployment script in background with proper detachment
                try:
                    # Use nohup and redirect to properly detach the process
                    subprocess.Popen([
                        'nohup', 'bash', DEPLOY_SCRIPT, 'webhook'
                    ], 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True  # This creates a new process group
                    )
                    logging.info("Auto-deployment script started in background with proper detachment")
                except Exception as e:
                    logging.error(f"Failed to start deployment: {e}")
            else:
                logging.info("Webhook received but not for main branch")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ignored", "message": "Not main branch"}).encode())
                
        except Exception as e:
            logging.error(f"Error processing webhook: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "port": WEBHOOK_PORT}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Override to use our logger
        logging.info(f"{self.address_string()} - {format % args}")

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', WEBHOOK_PORT), WebhookHandler)
    logging.info(f"Webhook server starting on port {WEBHOOK_PORT}")
    logging.info("Webhook URL: http://your-server-ip:9000/webhook")
    logging.info("Health check: http://your-server-ip:9000/health")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Webhook server shutting down")
        server.shutdown()
