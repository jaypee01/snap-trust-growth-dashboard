import sqlite3
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

# Database path
DB_PATH = Path(__file__).resolve().parent / ".." / "data" / "app.db"
DB_PATH = DB_PATH.resolve()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatRequest(BaseModel):
    prompt: str
    userType: str  # "consumer" or "merchant"

def _connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)

def get_consumer_data() -> str:
    """Get consumer-related data from the database"""
    with _connect() as conn:
        # Get payment data for consumers
        payments_df = pd.read_sql_query(
            """
            SELECT PaymentDate, PaymentAmount, PaymentStatus, CustomerID
            FROM payments
            ORDER BY PaymentDate DESC
            LIMIT 100
            """,
            conn,
            parse_dates=["PaymentDate"]
        )
        
        # Get monthly collections data
        monthly_df = pd.read_sql_query(
            """
            SELECT 
                strftime('%Y-%m', PaymentDate) as month,
                SUM(PaymentAmount) as total_amount,
                COUNT(CASE WHEN PaymentStatus = 'PAID' THEN 1 END) as paid_count,
                COUNT(CASE WHEN PaymentStatus = 'PENDING' THEN 1 END) as pending_count,
                COUNT(CASE WHEN PaymentStatus = 'FAILED' THEN 1 END) as failed_count
            FROM payments
            GROUP BY strftime('%Y-%m', PaymentDate)
            ORDER BY month DESC
            LIMIT 12
            """,
            conn
        )
        
        return f"""
Consumer Payment Data Summary:
- Total recent payments: {len(payments_df)}
- Payment status distribution: {payments_df['PaymentStatus'].value_counts().to_dict()}
- Average payment amount: ${payments_df['PaymentAmount'].mean():.2f}
- Recent monthly trends: {monthly_df.to_dict('records')}
- Date range: {payments_df['PaymentDate'].min()} to {payments_df['PaymentDate'].max()}
"""

def is_chart_request(prompt: str) -> bool:
    """Check if the user is requesting a chart/visualization"""
    chart_keywords = [
        "chart", "graph", "visualize", "plot", "line", "bar", "pie", "scatter",
        "histogram", "heatmap", "treemap", "radar", "sankey", "funnel", "gauge",
        "area", "bubble", "donut", "doughnut", "waterfall", "candlestick",
        "box", "violin", "ridge", "calendar", "chord", "network", "sunburst",
        "stream", "marimekko", "mosaic", "parallel", "sankey", "voronoi",
        "show", "display", "create", "generate", "make", "draw", "render"
    ]
    prompt_lower = prompt.lower()
    return any(word in prompt_lower for word in chart_keywords)

def generate_chart_code_with_openai(prompt: str, user_type: str, context_data: str) -> str:
    """Generate Nivo chart code using OpenAI based on user's specific request"""
    
    chart_system_prompt = f"""You are an expert React developer specializing in Nivo charts. 
    Generate ONLY the React component code for a Nivo chart based on the user's request.
    
    Available Nivo chart types: ResponsiveLine, ResponsiveBar, ResponsivePie
    
    Data Context for {user_type}:
    {context_data}
    
    Requirements:
    1. Generate a complete React component that can be directly used
    2. Use ONLY ResponsiveLine, ResponsiveBar, or ResponsivePie based on the user's request
    3. Include proper imports from @nivo/line, @nivo/bar, or @nivo/pie packages
    4. Make the component responsive with height: '400px', width: '100%'
    5. Use data prop for the chart data
    6. Include proper styling, legends, and tooltips
    7. Make it visually appealing with appropriate colors and themes
    8. Export as default export
    9. Do NOT include any explanations or markdown, ONLY the React code
    10. Component name should be descriptive based on the request
    11. For line charts, use ResponsiveLine from @nivo/line
    12. For bar charts, use ResponsiveBar from @nivo/bar  
    13. For pie charts, use ResponsivePie from @nivo/pie
    
    User Request: {prompt}
    
    Generate the React component code:"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": chart_system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fallback to a basic chart if OpenAI fails
        return generate_fallback_chart_code(prompt, user_type)

def generate_fallback_chart_code(prompt: str, user_type: str) -> str:
    """Generate a basic fallback chart code when OpenAI is not available"""
    return f'''import React from 'react';
import {{ ResponsiveBar }} from '@nivo/bar';

const GeneratedChart = ({{ data }}) => {{
  return (
    <div style={{ height: '400px', width: '100%' }}>
      <ResponsiveBar
        data={data}
        keys={['value']}
        indexBy="id"
        margin={{ top: 50, right: 130, bottom: 50, left: 60 }}
        padding={{0.3}}
        valueScale={{ type: 'linear' }}
        indexScale={{ type: 'band', round: true }}
        colors={{ scheme: 'nivo' }}
        axisTop={{null}}
        axisRight={{null}}
        axisBottom={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: 'Category',
          legendPosition: 'middle',
          legendOffset: 32
        }}
        axisLeft={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: 'Value',
          legendPosition: 'middle',
          legendOffset: -40
        }}
        labelSkipWidth={{12}}
        labelSkipHeight={{12}}
        role="application"
        ariaLabel="Generated Chart"
      />
    </div>
  );
}};

export default GeneratedChart;'''

def generate_fallback_response(prompt: str, user_type: str, context_data: str) -> str:
    """Generate a fallback response when OpenAI API is not available"""
    
    # Check if user wants a chart
    if is_chart_request(prompt):
        return generate_fallback_chart_code(prompt, user_type)
    
    # Simple keyword-based responses for non-chart requests
    if user_type == "consumer":
        if any(word in prompt_lower for word in ["trend", "pattern", "monthly", "collection"]):
            return """Based on the consumer payment data:

📊 **Payment Trends Analysis:**
- The data shows monthly payment collection patterns with both expected and received amounts
- Payment status distribution varies across different time periods
- Recent trends indicate fluctuations in payment success rates

💡 **Key Insights:**
- Monitor monthly collection rates to identify seasonal patterns
- Track payment status changes over time for better forecasting
- Consider implementing automated payment reminders for better collection rates

📈 **Recommendations:**
- Analyze peak payment months to optimize collection strategies
- Review failed payment patterns to improve success rates
- Consider offering flexible payment options during low collection periods

*Note: This is a fallback response. For more detailed AI analysis, please check your OpenAI API quota.*"""
        
        elif any(word in prompt_lower for word in ["failure", "failed", "error", "problem"]):
            return """Based on the consumer payment data:

⚠️ **Payment Failure Analysis:**
- Payment failures are tracked in the system with different status codes
- Failed payments impact overall collection rates and revenue
- Understanding failure patterns helps improve payment success

🔍 **Common Failure Patterns:**
- Technical issues during payment processing
- Insufficient funds or expired payment methods
- Network connectivity problems
- Invalid payment information

💡 **Improvement Strategies:**
- Implement retry mechanisms for failed payments
- Send timely notifications for payment failures
- Provide multiple payment options to reduce failure rates
- Regular validation of payment information

*Note: This is a fallback response. For more detailed AI analysis, please check your OpenAI API quota.*"""
        
        else:
            return f"""Based on the consumer payment data:

📊 **Consumer Payment Overview:**
{context_data}

💡 **General Insights:**
- Consumer payment patterns show various trends and behaviors
- Payment success rates vary across different time periods
- Monthly collections provide insights into consumer payment habits

📈 **Key Metrics:**
- Payment status distribution across different categories
- Average payment amounts and frequency
- Collection trends over time

*Note: This is a fallback response. For more detailed AI analysis, please check your OpenAI API quota.*"""
    
    else:  # merchant
        if any(word in prompt_lower for word in ["performance", "best", "top", "ranking"]):
            return """Based on the merchant performance data:

🏆 **Top Performing Merchants:**
- Merchants are ranked by payment volume and transaction success rates
- Performance metrics include trust scores, engagement, and compliance
- Top merchants show consistent payment collection and customer satisfaction

📊 **Performance Metrics:**
- Payment volume and transaction counts
- Trust scores based on repayment rates and dispute resolution
- Engagement and compliance scores
- Customer satisfaction indicators

💡 **Success Factors:**
- High repayment rates and low dispute rates
- Strong customer engagement and responsiveness
- Compliance with payment terms and conditions
- Consistent transaction volume growth

*Note: This is a fallback response. For more detailed AI analysis, please check your OpenAI API quota.*"""
        
        elif any(word in prompt_lower for word in ["trust", "score", "loyalty", "reputation"]):
            return """Based on the merchant trust and loyalty data:

⭐ **Trust Score Analysis:**
- Trust scores are calculated based on multiple factors
- Higher scores indicate better merchant reliability and performance
- Trust scores influence merchant rankings and recommendations

🔍 **Trust Score Components:**
- Repayment rates and payment success
- Dispute resolution and customer satisfaction
- Transaction volume and consistency
- Compliance with terms and conditions
- Responsiveness to customer needs

📈 **Improvement Areas:**
- Focus on reducing dispute rates
- Improve payment success rates
- Enhance customer engagement
- Maintain high compliance standards

*Note: This is a fallback response. For more detailed AI analysis, please check your OpenAI API quota.*"""
        
        else:
            return f"""Based on the merchant data:

📊 **Merchant Performance Overview:**
{context_data}

💡 **Key Insights:**
- Merchant performance varies across different metrics
- Trust scores and loyalty tiers indicate merchant reliability
- Payment success rates reflect merchant quality

📈 **Performance Indicators:**
- Payment volume and transaction counts
- Trust scores and loyalty ratings
- Customer satisfaction metrics
- Compliance and engagement scores

*Note: This is a fallback response. For more detailed AI analysis, please check your OpenAI API quota.*"""

def get_merchant_data() -> str:
    """Get merchant-related data from the database"""
    with _connect() as conn:
        # Get merchant payment data
        merchant_payments_df = pd.read_sql_query(
            """
            SELECT 
                MerchantName,
                SUM(PaymentAmount) as total_amount,
                COUNT(*) as payment_count,
                COUNT(CASE WHEN PaymentStatus = 'PAID' THEN 1 END) as paid_count,
                COUNT(CASE WHEN PaymentStatus = 'PENDING' THEN 1 END) as pending_count,
                COUNT(CASE WHEN PaymentStatus = 'FAILED' THEN 1 END) as failed_count
            FROM payments
            GROUP BY MerchantName
            ORDER BY total_amount DESC
            LIMIT 20
            """,
            conn
        )
        
        # Get merchant loyalty data
        loyalty_df = pd.read_sql_query(
            """
            SELECT 
                MerchantName,
                RepaymentRate,
                DisputeRate,
                DefaultRate,
                TransactionVolume,
                EngagementScore,
                ComplianceScore,
                ResponsivenessScore,
                ExclusivityFlag
            FROM merchants_loyalty
            ORDER BY TransactionVolume DESC
            LIMIT 20
            """,
            conn
        )
        
        return f"""
Merchant Data Summary:
- Top merchants by payment volume: {merchant_payments_df.head(10).to_dict('records')}
- Merchant loyalty metrics: {loyalty_df.head(10).to_dict('records')}
- Total unique merchants: {len(merchant_payments_df)}
- Average payment per merchant: ${merchant_payments_df['total_amount'].mean():.2f}
- Payment success rate: {(merchant_payments_df['paid_count'] / merchant_payments_df['payment_count'] * 100).mean():.1f}%
"""

@router.post("/chat")
async def chat_with_ai(request: ChatRequest) -> Dict[str, Any]:
    """
    Send a prompt to OpenAI with relevant data context based on user type.
    """
    try:
        # Get relevant data based on user type
        if request.userType == "consumer":
            context_data = get_consumer_data()
            system_prompt = """You are an AI assistant specialized in analyzing consumer payment data and trends. 
            You help users understand payment patterns, identify trends, and provide insights about consumer behavior.
            Use the provided data context to answer questions accurately and provide actionable insights."""
        elif request.userType == "merchant":
            context_data = get_merchant_data()
            system_prompt = """You are an AI assistant specialized in analyzing merchant performance data, trust scores, and business metrics.
            You help merchants understand their performance, identify opportunities for growth, and provide business insights.
            Use the provided data context to answer questions accurately and provide actionable recommendations."""
        else:
            raise HTTPException(status_code=400, detail="Invalid userType. Must be 'consumer' or 'merchant'")
        
        # Check if user wants a chart
        if is_chart_request(request.prompt):
            # Generate chart code using OpenAI
            chart_code = generate_chart_code_with_openai(request.prompt, request.userType, context_data)
            return {
                "response": chart_code,
                "userType": request.userType,
                "status": "chart_code",
                "isChart": True
            }
        
        # Prepare the full prompt with context for regular responses
        full_prompt = f"""
{system_prompt}

Data Context:
{context_data}

User Question: {request.prompt}

Please provide a detailed, helpful response based on the data context provided. If the question cannot be answered with the available data, please explain what information would be needed.
"""
        
        # Check if OpenAI API key is available and has quota
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
            # Fallback response when no API key or quota exceeded
            fallback_response = generate_fallback_response(request.prompt, request.userType, context_data)
            return {
                "response": fallback_response,
                "userType": request.userType,
                "status": "fallback",
                "note": "Using fallback response - OpenAI API not available"
            }
        
        try:
            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return {
                "response": response.choices[0].message.content,
                "userType": request.userType,
                "status": "success"
            }
        except openai.APIError as e:
            if "quota" in str(e).lower() or "429" in str(e):
                # Fallback response when quota exceeded
                fallback_response = generate_fallback_response(request.prompt, request.userType, context_data)
                return {
                    "response": fallback_response,
                    "userType": request.userType,
                    "status": "fallback",
                    "note": "Using fallback response - OpenAI quota exceeded"
                }
            else:
                raise e
        
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e

@router.get("/health")
async def health_check():
    """Health check endpoint for AI service"""
    return {"status": "healthy", "service": "ai-chat"}
