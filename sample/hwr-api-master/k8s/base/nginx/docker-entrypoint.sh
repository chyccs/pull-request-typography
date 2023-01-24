#!/bin/bash

# Wait for uvicorn
chmod +x /wait-for-it.sh
/wait-for-it.sh 127.0.0.1:8000 --timeout=0 -- nginx -g 'daemon off;'