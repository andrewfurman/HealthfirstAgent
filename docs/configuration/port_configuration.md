# Port Configuration

## Overview

The Healthfirst Agent application is configured to run on different ports depending on the environment to avoid conflicts and match deployment requirements.

## Local Development

**Default Port**: `8001`

The application defaults to port 8001 for local development to avoid conflicts with Docker and other services that commonly use ports 8000 and 8080.

To run locally:
```bash
poetry run python main.py  # Runs on port 8001 by default
```

To override the port locally:
```bash
PORT=3000 poetry run python main.py  # Runs on port 3000
```

## Azure Deployment

**Port**: `8000`

For Azure deployment, set the `PORT` environment variable to `8000`:
```bash
PORT=8000
```

Azure App Service will automatically set this environment variable when configured properly.

## Port Priority

The application checks for ports in this order:
1. `PORT` environment variable (if set)
2. Default to `8001` (for local development)

## Code Configuration

In `main.py`:
```python
# Use environment variable for port if available, default to 8001 to avoid Docker conflict
# In Azure deployment, set PORT=8000 environment variable
port = int(os.environ.get('PORT', 8001))
```

## Common Port Conflicts

If you encounter a "Port already in use" error:

1. **Check what's using the port**:
   ```bash
   lsof -i :8001  # Check port 8001
   ```

2. **Kill the process** (if safe to do so):
   ```bash
   kill <PID>
   ```

3. **Or use a different port**:
   ```bash
   PORT=8100 poetry run python main.py
   ```

## Docker Considerations

Docker Desktop often uses ports 8000-8010. If you're running Docker, the application will default to port 8001 to avoid conflicts.

## URLs by Environment

- **Local Development**: http://127.0.0.1:8001
- **Azure Deployment**: https://your-app.azurewebsites.net (port 8000 internally)

## Troubleshooting

### Port Already in Use
```bash
# Find what's using a port
lsof -i :8001

# Find all Python processes
ps aux | grep python

# Kill a specific process
kill <PID>
```

### Testing Different Ports
```bash
# Test if a port is available
nc -zv localhost 8001

# Start on a specific port
PORT=9000 poetry run python main.py
```