#!/bin/sh

# Calculate the number of workers based on available CPU cores
WORKERS=$(python -c "import multiprocessing as mp; print((mp.cpu_count() * 2) + 1)")



# Print the calculated number of workers for debugging
echo "Calculated number of workers: $WORKERS" | tee /tmp/debug.log

# Start Gunicorn with the calculated number of workers
exec gunicorn "app:create_app()" \
  --bind 0.0.0.0:8000 \
  --workers $WORKERS \
  --timeout 120