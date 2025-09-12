# AI Chat Setup Instructions

## Environment Variables

To use the AI chat functionality, you need to set up your OpenAI API key:

1. Create a `.env` file in the backend directory:
```bash
cd /Users/neelkhalade/hackathon/snap-trust-growth-dashboard/backend
touch .env
```

2. Add your OpenAI API key to the `.env` file:
```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

3. Get your OpenAI API key from: https://platform.openai.com/api-keys

## Running the Backend

1. Activate the virtual environment:
```bash
source venv/bin/activate
```

2. Install dependencies (if not already installed):
```bash
pip install -r requirements.txt
```

3. Run the FastAPI server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing the AI Endpoint

You can test the AI chat endpoint using curl:

```bash
# Test consumer chat
curl -X POST "http://localhost:8000/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What are the payment trends for consumers?", "userType": "consumer"}'

# Test merchant chat
curl -X POST "http://localhost:8000/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Which merchants are performing best?", "userType": "merchant"}'
```

## Features

- **Consumer Dashboard**: Ask questions about consumer payment patterns, trends, and insights
- **Merchant Dashboard**: Ask questions about merchant performance, trust scores, and business metrics
- **Context-Aware**: AI responses are based on actual data from your database
- **Real-time**: Responses are generated in real-time using OpenAI's API
