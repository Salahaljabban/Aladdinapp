
#!/usr/bin/env python3
"""
Aladdin GRC - Governance, Risk, and Compliance Management System
Main application entry point
"""

from app import create_app
import os

if __name__ == '__main__':
    app = create_app()
    
    # Get host and port from environment or use defaults
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print("=" * 50)
    print("🧞‍♂️ Aladdin GRC System Starting...")
    print("=" * 50)
    print(f"🌐 Server: http://{host}:{port}")
    print(f"🔧 Debug Mode: {debug}")
    print("=" * 50)
    
    app.run(host=host, port=port, debug=debug)
