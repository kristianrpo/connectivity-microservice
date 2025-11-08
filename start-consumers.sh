#!/bin/bash
set -e

echo "Starting RabbitMQ consumers..."

# Start document authentication consumer in background
echo "Starting document authentication consumer..."
python manage.py consume_document_auth &
PID1=$!

# Start auth events consumer in background
echo "Starting auth events consumer..."
python manage.py consume_auth_events &
PID2=$!

echo "Both consumers started"
echo "  Document auth consumer PID: $PID1"
echo "  Auth events consumer PID: $PID2"

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
