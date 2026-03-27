"""
Start script for OmniSyntax REST API
"""

import os
import sys

import uvicorn

def main():
    """Start the API server"""
    print("="* 60)
    print("🚀 Starting OmniSyntax REST API")
    print("=" * 60)
    print("\n📡 API will be available at:")
    print("   - Main: http://localhost:8000")
    print("   - Docs: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("\n⚡ Press CTRL+C to stop the server")
    print("=" * 60)
    print()
    
    # Configuration
    config = {
        "app": "api:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,  # Auto-reload on code changes
        "log_level": "info",
    }
    
    # Check if running in production
    if os.getenv("PRODUCTION", "false").lower() == "true":
        config["reload"] = False
        config["workers"] = 4
        print("🏭 Running in PRODUCTION mode")
    else:
        print("🔧 Running in DEVELOPMENT mode (auto-reload enabled)")
    
    print()
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n\n✅ API server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error starting API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
