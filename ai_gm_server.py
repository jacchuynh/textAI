#!/usr/bin/env python3
"""
AI GM Brain API Server
Simple test version that provides basic fallback functionality
"""

import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_gm_server")

class AIGMHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for AI GM Brain requests."""
    
    def do_GET(self):
        """Handle GET requests."""
        path = urlparse(self.path).path
        
        if path == '/':
            self.send_json_response({
                "service": "TextRealmsAI - AI GM Brain API",
                "status": "running",
                "ai_gm_available": True,
                "version": "simple-test"
            })
        elif path == '/health':
            self.send_json_response({"status": "healthy", "ai_gm_available": True})
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests."""
        path = urlparse(self.path).path
        
        if path == '/api/ai-gm/process-input':
            self.handle_process_input()
        else:
            self.send_error(404, "Not Found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.add_cors_headers()
        self.end_headers()
    
    def add_cors_headers(self):
        """Add CORS headers to response."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def send_json_response(self, data, status=200):
        """Send a JSON response."""
        self.send_response(status)
        self.add_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def handle_process_input(self):
        """Handle player input processing."""
        try:
            # Read request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode())
            
            # Extract input text
            input_text = request_data.get('input_text', '').lower().strip()
            player_id = request_data.get('player_id', 'unknown')
            
            logger.info(f"Processing input from {player_id}: '{input_text}'")
            
            # Simple command processing with enhanced responses
            response = self.process_command(input_text, request_data)
            
            self.send_json_response(response)
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            self.send_json_response({
                "response_text": "I'm having trouble processing your request right now. Please try again.",
                "success": False,
                "metadata": {"error": str(e)}
            }, 500)
    
    def process_command(self, input_text, request_data):
        """Process the command and return appropriate response."""
        
        # Question patterns for spells
        if any(pattern in input_text for pattern in [
            'what spells', 'which spells', 'spell', 'magic', 'cast'
        ]):
            player_context = request_data.get('player_context', {})
            magic_profile = player_context.get('magic_profile', {})
            
            if magic_profile:
                affinity = magic_profile.get('magicAffinity', 'unknown')
                aspects = magic_profile.get('knownAspects', ['basic'])
                spell_power = magic_profile.get('spellPower', 10)
                
                response_text = f"As a {affinity} magic user, you know spells from these aspects: {', '.join(aspects)}. "
                response_text += f"Your current spell power is {spell_power}. "
                response_text += "You can cast spells like 'arcane missile', 'basic heal', or 'light' depending on your aspects. "
                response_text += "Try commands like 'cast arcane missile' or 'cast light'."
            else:
                response_text = "You don't seem to have any magical training yet. Explore the world to learn magic!"
            
            return {
                "response_text": response_text,
                "success": True,
                "metadata": {
                    "processing_mode": "QUESTION_RESPONSE",
                    "complexity": "CONVERSATIONAL",
                    "parsed_successfully": True
                }
            }
        
        # Help/guidance requests
        if any(pattern in input_text for pattern in [
            'help', 'what can i do', 'how do i', 'commands'
        ]):
            return {
                "response_text": "You can try commands like: 'look around', 'inventory', 'go [direction]', 'cast [spell]', 'examine [item]', or ask questions like 'what spells can I cast?' or 'where am I?'",
                "success": True,
                "metadata": {
                    "processing_mode": "HELP_RESPONSE",
                    "complexity": "SIMPLE_COMMAND"
                }
            }
        
        # Location questions
        if any(pattern in input_text for pattern in [
            'where am i', 'where are we', 'what is this place', 'location'
        ]):
            player_context = request_data.get('player_context', {})
            region = player_context.get('location_region', 'Unknown Region')
            area = player_context.get('location_area', 'Unknown Area')
            
            return {
                "response_text": f"You are currently in {area} within the {region} region. The air here feels charged with mystical energies.",
                "success": True,
                "metadata": {
                    "processing_mode": "LOCATION_RESPONSE",
                    "complexity": "CONVERSATIONAL"
                }
            }
        
        # Basic command processing
        if input_text.startswith('look'):
            return {
                "response_text": "You look around carefully, taking in your surroundings. The area seems peaceful but full of hidden mysteries.",
                "success": True,
                "metadata": {"processing_mode": "BASIC_COMMAND"}
            }
        
        if input_text.startswith('inventory'):
            return {
                "response_text": "You check your belongings. You have some basic equipment and supplies for your journey.",
                "success": True,
                "metadata": {"processing_mode": "BASIC_COMMAND"}
            }
        
        # Default response for unrecognized input with LLM flag
        return {
            "response_text": "I understand you're trying to do something, but I'm not quite sure what. This would normally be processed by the advanced AI system. Try asking specific questions or using commands like 'look', 'inventory', or 'help'.",
            "success": True,
            "requires_llm": True,
            "metadata": {
                "processing_mode": "NEEDS_LLM",
                "complexity": "COMPLEX",
                "suggested_upgrade": "This response would be much better with the full AI GM Brain system"
            }
        }

def run_server(host='127.0.0.1', port=8000):
    """Run the AI GM Brain server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, AIGMHandler)
    
    print(f"🧠 AI GM Brain API server running on http://{host}:{port}")
    print("📝 This is a simple test version. For full functionality, implement the Python AI GM Brain integration.")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
