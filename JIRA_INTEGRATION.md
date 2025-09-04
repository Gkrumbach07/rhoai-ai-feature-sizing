# Jira Integration Setup

This document explains how to set up and use the direct Jira API integration for creating RFE issues from the React component.

## Quick Setup

### 1. Configure Environment Variables

Copy the environment template and configure Jira settings:

```bash
cp env.template .env
```

Edit `.env` and configure the Jira section:

```env
# Jira Integration Configuration
JIRA_BASE_URL=https://issues.redhat.com
JIRA_PROJECT_KEY=RHOAI
JIRA_USERNAME=your_jira_username_here
JIRA_API_TOKEN=your_jira_api_token_here
JIRA_DEFAULT_ASSIGNEE=your_username

# API Server Configuration
REACT_APP_API_URL=http://localhost:8001
```

### 2. Get Jira API Token

1. Go to your Jira account settings: [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Create a new API token
3. Copy the token and add it to your `.env` file as `JIRA_API_TOKEN`

### 3. Install Dependencies

Make sure you have the required Python dependencies:

```bash
pip install fastapi uvicorn aiohttp
```

### 4. Start the API Server

```bash
python start_api.py
```

This will start the API server on `http://localhost:8001`.

## Usage

### Creating RFE Issues

1. **Generate Artifacts**: Use the RFE builder workflow to generate RFE and feature refinement documents
2. **Create RFE Button**: After artifacts are generated, a "Create RFE in Jira" button will appear
3. **Click to Create**: Click the button to create the RFE as a Jira Story
4. **Success**: The issue will be created and automatically open in a new browser tab

### API Endpoints

The API server provides these endpoints:

- `POST /api/create-rfe` - Create a new RFE issue in Jira
- `GET /api/health` - Health check endpoint
- `GET /` - API information

### Example API Request

```bash
curl -X POST "http://localhost:8001/api/create-rfe" \
  -H "Content-Type: application/json" \
  -d '{
    "rfe_content": "# My RFE\nThis is the RFE description...",
    "refinement_content": "## Refined Requirements\nDetailed requirements...",
    "issue_type": "Story",
    "priority": "Medium"
  }'
```

## Configuration Options

### Jira Settings

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `JIRA_BASE_URL` | `https://issues.redhat.com` | Your Jira instance URL |
| `JIRA_PROJECT_KEY` | `RHOAI` | Project key where RFEs should be created |
| `JIRA_USERNAME` | - | Your Jira username (required) |
| `JIRA_API_TOKEN` | - | Your Jira API token (required) |
| `JIRA_DEFAULT_ASSIGNEE` | - | Default assignee for RFEs (optional) |

### API Server Settings

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8001` | API server port |
| `REACT_APP_API_URL` | `http://localhost:8001` | Frontend API URL |

## Issue Template

Created RFE issues will include:

- **Summary**: Extracted from the first heading or line of the RFE content
- **Description**: Formatted with both RFE description and feature refinement content
- **Issue Type**: Story (configurable)
- **Priority**: Medium (configurable)
- **Labels**: `rfe`, `ai-generated`, `feature-request`

## Troubleshooting

### Common Issues

1. **"Jira credentials not configured"**
   - Ensure `JIRA_USERNAME` and `JIRA_API_TOKEN` are set in `.env`

2. **"Network error. Please check if the API server is running."**
   - Start the API server: `python start_api.py`
   - Check that port 8001 is available

3. **Jira API authentication errors**
   - Verify your API token is valid
   - Check that your username is correct
   - Ensure you have permission to create issues in the target project

4. **Project not found**
   - Verify the `JIRA_PROJECT_KEY` exists and you have access
   - Check that the project allows the specified issue type (Story)

### Logs

Check the API server logs for detailed error information:

```bash
python start_api.py
# API logs will appear in the console
```

## Security Notes

- **API Tokens**: Keep your Jira API token secure and don't commit it to version control
- **CORS**: The API server allows all origins by default. In production, configure specific origins
- **HTTPS**: In production, use HTTPS for the API server and configure proper SSL certificates

## Development

### Testing the API

Test the API server directly:

```bash
# Health check
curl http://localhost:8001/api/health

# Create test RFE
curl -X POST "http://localhost:8001/api/create-rfe" \
  -H "Content-Type: application/json" \
  -d '{
    "rfe_content": "# Test RFE\nThis is a test request.",
    "refinement_content": "## Test Refinement\nTest details."
  }'
```

### Frontend Development

The React component will automatically detect and use the API server. Make sure:

1. `REACT_APP_API_URL` is set correctly in your `.env`
2. The API server is running on the specified URL
3. CORS is configured to allow your frontend domain
