#!/usr/bin/env python3
"""Simple script to run the FastAPI server with uvicorn."""
import uvicorn
import sys

if __name__ == '__main__':
    uvicorn.run(
        'server:app',
        host='127.0.0.1',
        port=8001,
        reload=False,
        log_level='info',
    )
