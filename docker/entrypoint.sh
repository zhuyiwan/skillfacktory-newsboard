#!/bin/sh

# Apply database migrations
echo "Running Celery..."
celery -A CRM worker -l info