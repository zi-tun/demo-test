"""
Data Agent for data analysis, visualization, and statistical tasks.
Specializes in data processing, analysis, visualization, and insights generation.
"""

from typing import List

from agents.base_agent import BaseAgent
from core.state import WorkflowState, AgentType
from utils.llm_client import LLMMessage


class DataAgent(BaseAgent):
    """Specialized agent for data analysis and visualization tasks."""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.DATA,
            name="Data Agent",
            description="Specializes in data analysis, visualization, and statistical insights"
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the data agent."""
        return """You are a Data Agent, an expert in data analysis, statistics, and visualization. Your capabilities include:

CORE DATA FUNCTIONS:
- Data analysis and statistical modeling
- Data visualization and charting
- Database queries and data manipulation
- Exploratory data analysis (EDA)
- Statistical testing and hypothesis validation
- Predictive modeling and machine learning
- Reporting and insights generation

DATA ANALYSIS SPECIALIZATIONS:
- Descriptive statistics and summaries
- Correlation and regression analysis
- Time series analysis and forecasting
- A/B testing and experimental design
- Classification and clustering
- Anomaly detection and outlier analysis
- Performance metrics and KPI tracking

VISUALIZATION EXPERTISE:
- Charts: bar, line, scatter, histogram, box plots
- Advanced: heatmaps, treemaps, network graphs
- Interactive dashboards and reports
- Statistical plots: QQ plots, residual plots
- Geographic and spatial visualizations
- Time series and trend visualizations

DATA PROCESSING TOOLS:
- Python: pandas, numpy, matplotlib, seaborn, plotly
- R: ggplot2, dplyr, tidyr, shiny
- SQL: PostgreSQL, MySQL, SQLite, BigQuery
- Excel: pivot tables, formulas, charts
- Tableau, Power BI for business intelligence

ANALYSIS METHODOLOGY:
1. Understand the business question or hypothesis
2. Assess data quality and completeness
3. Perform exploratory data analysis
4. Apply appropriate statistical methods
5. Validate results and check assumptions
6. Generate actionable insights and recommendations
7. Create clear visualizations and reports

BEST PRACTICES:
- Always validate data quality and assumptions
- Use appropriate statistical methods for the data type
- Consider confounding variables and biases
- Provide confidence intervals and significance levels
- Make visualizations clear and interpretable
- Translate findings into business language

RESPONSE FORMAT:
- Start with key findings and insights
- Provide methodology and assumptions
- Include data quality assessments
- Suggest appropriate visualizations
- Recommend next steps or further analysis
- Note limitations and potential biases

Always ensure statistical rigor while making insights accessible to non-technical stakeholders."""
    
    def process_request(self, state: WorkflowState) -> WorkflowState:
        """Process data analysis requests with specialized analytical methodology."""
        try:
            # Analyze the data task
            analysis_type = self._analyze_data_task(state.current_user_input)
            data_context = self._extract_data_context(state.current_user_input)
            
            # Build specialized data analysis prompt
            messages = self._build_data_messages(state, analysis_type, data_context)
            
            # Generate analysis with appropriate precision
            temperature = 0.2 if analysis_type in ['statistical_testing', 'validation'] else 0.4
            response = self.generate_response(messages, temperature=temperature)
            
            # Postprocess with data-specific formatting
            formatted_response = self.postprocess_response(state, response)
            
            # Update state with data context
            state.task_context['analysis_type'] = analysis_type
            state.task_context['data_context'] = data_context
            
            return self.update_state_with_response(state, formatted_response)
            
        except Exception as e:
            return self.handle_error(state, e)
    
    def _analyze_data_task(self, user_input: str) -> str:
        """Analyze what type of data task is being requested."""
        input_lower = user_input.lower()
        
        if any(term in input_lower for term in ['visualize', 'chart', 'plot', 'graph', 'dashboard']):
            return 'visualization'
        elif any(term in input_lower for term in ['statistics', 'statistical', 'significance', 'test']):
            return 'statistical_analysis'
        elif any(term in input_lower for term in ['correlation', 'relationship', 'association']):
            return 'correlation_analysis'
        elif any(term in input_lower for term in ['trend', 'time series', 'forecast', 'predict']):
            return 'time_series'
        elif any(term in input_lower for term in ['segment', 'cluster', 'group', 'classify']):
            return 'clustering_classification'
        elif any(term in input_lower for term in ['sql', 'query', 'database', 'table']):
            return 'database_query'
        elif any(term in input_lower for term in ['clean', 'preprocess', 'transform', 'prepare']):
            return 'data_preprocessing'
        elif any(term in input_lower for term in ['summary', 'describe', 'overview', 'profile']):
            return 'descriptive_analysis'
        elif any(term in input_lower for term in ['outlier', 'anomaly', 'unusual', 'detect']):
            return 'anomaly_detection'
        else:
            return 'general_analysis'
    
    def _extract_data_context(self, user_input: str) -> dict:
        """Extract data context and constraints from user input."""
        context = {
            'data_size': 'unknown',
            'data_type': 'unknown',
            'tools_mentioned': [],
            'constraints': []
        }
        
        input_lower = user_input.lower()
        
        # Extract data size hints
        if any(term in input_lower for term in ['large', 'big data', 'millions', 'thousands']):
            context['data_size'] = 'large'
        elif any(term in input_lower for term in ['small', 'few', 'limited']):
            context['data_size'] = 'small'
        
        # Extract data type hints
        if any(term in input_lower for term in ['sales', 'revenue', 'financial']):
            context['data_type'] = 'financial'
        elif any(term in input_lower for term in ['customer', 'user', 'behavior']):
            context['data_type'] = 'behavioral'
        elif any(term in input_lower for term in ['web', 'clicks', 'views', 'traffic']):
            context['data_type'] = 'web_analytics'
        elif any(term in input_lower for term in ['survey', 'feedback', 'rating']):
            context['data_type'] = 'survey'
        
        # Extract tool preferences
        tools = ['python', 'r', 'sql', 'excel', 'tableau', 'powerbi']
        for tool in tools:
            if tool in input_lower:
                context['tools_mentioned'].append(tool)
        
        return context
    
    def _build_data_messages(self, state: WorkflowState, analysis_type: str, data_context: dict) -> List[LLMMessage]:
        """Build specialized messages for data analysis requests."""
        messages = [LLMMessage("system", self.get_system_prompt())]
        
        # Add analysis-specific guidance
        type_guidance = self._get_analysis_type_guidance(analysis_type, data_context)
        if type_guidance:
            messages.append(LLMMessage("system", f"SPECIFIC GUIDANCE FOR {analysis_type.upper()}:\n{type_guidance}"))
        
        # Add user request with context
        context = state.get_conversation_context()
        if context:
            user_message = f"Previous conversation:\n{context}\n\nData Analysis Request: {state.current_user_input}"
        else:
            user_message = f"Data Analysis Request: {state.current_user_input}"
        
        messages.append(LLMMessage("user", user_message))
        
        return messages
    
    def _get_analysis_type_guidance(self, analysis_type: str, data_context: dict) -> str:
        """Get specific guidance for different analysis types."""
        guidance_map = {
            'visualization': """
- Choose appropriate chart types for the data and message
- Ensure visualizations are clear and interpretable
- Include proper labels, titles, and legends
- Consider color accessibility and design principles
- Suggest interactive elements when appropriate
""",
            'statistical_analysis': """
- Check assumptions before applying statistical tests
- Choose appropriate tests for the data type and distribution
- Report effect sizes along with p-values
- Include confidence intervals where applicable
- Interpret results in practical terms
""",
            'time_series': """
- Check for trends, seasonality, and stationarity
- Consider appropriate forecasting methods
- Validate model assumptions and performance
- Account for external factors and events
- Provide prediction intervals for forecasts
""",
            'clustering_classification': """
- Determine optimal number of clusters or classes
- Evaluate model performance with appropriate metrics
- Consider feature selection and dimensionality reduction
- Validate results with business understanding
- Interpret clusters or classes meaningfully
""",
            'database_query': """
- Write efficient and optimized SQL queries
- Consider indexing and performance implications
- Include proper joins and aggregations
- Add data quality checks and validation
- Format results clearly and logically
"""
        }
        
        guidance = guidance_map.get(analysis_type, "")
        
        # Add context-specific guidance
        if data_context['data_size'] == 'large':
            guidance += "\n- Consider sampling strategies for large datasets"
            guidance += "\n- Optimize for performance and memory usage"
        
        if data_context['tools_mentioned']:
            tools_str = ', '.join(data_context['tools_mentioned'])
            guidance += f"\n- Prioritize solutions using: {tools_str}"
        
        return guidance
    
    def can_handle_request(self, user_input: str, intent: str) -> bool:
        """Check if this agent can handle the data analysis request."""
        data_keywords = [
            'data', 'analysis', 'statistics', 'chart', 'graph', 'plot',
            'visualize', 'database', 'sql', 'trend', 'correlation',
            'forecast', 'predict', 'cluster', 'segment', 'excel'
        ]
        
        input_lower = user_input.lower()
        return any(keyword in input_lower for keyword in data_keywords)
    
    def get_capabilities(self) -> List[str]:
        """Get data agent capabilities."""
        return [
            "Statistical analysis and hypothesis testing",
            "Data visualization and charting",
            "Correlation and regression analysis",
            "Time series analysis and forecasting",
            "Clustering and classification",
            "Database queries and data manipulation",
            "Exploratory data analysis (EDA)",
            "A/B testing and experimental design",
            "Anomaly detection and outlier analysis",
            "Performance metrics and KPI tracking"
        ]
    
    def postprocess_response(self, state: WorkflowState, response: str) -> str:
        """Add data-specific formatting to the response."""
        analysis_type = state.task_context.get('analysis_type', 'general_analysis')
        data_context = state.task_context.get('data_context', {})
        
        # Add analysis context note
        if analysis_type != 'general_analysis':
            context_note = f"\n\n📊 **Analysis Type**: {analysis_type.replace('_', ' ').title()}"
            response += context_note
        
        # Add data validation reminder
        if analysis_type in ['statistical_analysis', 'time_series', 'clustering_classification']:
            validation_note = "\n\n⚠️ **Important**: Please validate assumptions and data quality before implementing these recommendations."
            response += validation_note
        
        # Add tool suggestions if not specified
        if not data_context.get('tools_mentioned'):
            tool_note = "\n\n🛠️ **Suggested Tools**: Consider using Python (pandas, matplotlib), R (ggplot2), or Excel depending on your technical requirements."
            response += tool_note
        
        return response
    
    def get_fallback_response(self, state: WorkflowState, error: Exception) -> str:
        """Generate fallback response for data analysis errors."""
        return (
            "I apologize, but I encountered an issue while processing your data analysis request. "
            "This might be due to the complexity of the analysis or technical limitations. "
            "Could you try:\n"
            "1. Providing more details about your dataset structure\n"
            "2. Clarifying the specific analysis or insights you need\n"
            "3. Specifying your preferred tools or constraints\n"
            "4. Breaking down complex analyses into smaller steps\n\n"
            "I'm here to help with your data analysis needs once we resolve this issue."
        )
