import pandas as pd
import numpy as np
from datetime import datetime
import os
from openai import OpenAI

class FinancialAnalysisAgent:
    def __init__(self, df):
        self.df = df
        self.ai_initialized = False
        
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.ai_initialized = True
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
    
    def query(self, question):
        """Process a query about the data"""
        if not self.ai_initialized:
            return {
                'success': False,
                'error': 'AI not initialized. Please check OpenAI API key.'
            }
        
        try:
            # Prepare context
            context = self._prepare_context()
            
            # Create prompt
            prompt = f"""
            As a financial analysis expert, analyze the following transaction data and answer the question.
            
            Context:
            {context}
            
            Question: {question}
            
            Provide a clear, concise answer focusing on key insights and actionable recommendations.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            return {
                'success': True,
                'response': response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error in analysis: {str(e)}"
            }
    
    def get_smart_insights(self, df):
        """Generate smart insights from the data"""
        insights = []
        
        # High failure rate insight
        failure_rate = df['is_failed'].mean()
        if failure_rate > 0.15:
            insights.append({
                'type': 'warning',
                'title': 'High Transaction Failure Rate',
                'content': f'Current failure rate is {failure_rate*100:.1f}%, which is above the critical threshold of 15%.',
                'recommendation': 'Implement immediate measures to reduce failure rate, including infrastructure scaling and payment gateway optimization.'
            })
        
        # Branch performance insights
        branch_failure = df.groupby('branch_name')['is_failed'].mean()
        high_fail_branches = branch_failure[branch_failure > 0.2].index.tolist()
        
        if high_fail_branches:
            insights.append({
                'type': 'warning',
                'title': 'Branch Performance Alert',
                'content': f'Branches {", ".join(high_fail_branches)} have failure rates exceeding 20%.',
                'recommendation': 'Investigate branch-specific issues and consider routing transactions through alternative gateways.'
            })
        
        # Time pattern insights
        hourly_failure = df.groupby('hour')['is_failed'].mean()
        peak_hours = hourly_failure.nlargest(3).index.tolist()
        
        insights.append({
            'type': 'insight',
            'title': 'Peak Failure Hours Identified',
            'content': f'Highest failure rates occur during hours {", ".join(map(str, peak_hours))} with rates around {hourly_failure[peak_hours].mean()*100:.1f}%.',
            'recommendation': 'Schedule maintenance outside these hours and implement auto-scaling during peak times.'
        })
        
        # Revenue impact insight
        failed_amount = df[df['is_failed']]['transaction_amount'].sum()
        total_amount = df['transaction_amount'].sum()
        impact_percentage = (failed_amount / total_amount) * 100
        
        if impact_percentage > 5:
            insights.append({
                'type': 'warning',
                'title': 'Significant Revenue Impact',
                'content': f'Failed transactions represent {impact_percentage:.1f}% of total revenue (${failed_amount:,.2f}).',
                'recommendation': 'Prioritize fixing high-value transaction failures and implement retry mechanisms.'
            })
        
        # Transaction pattern insights
        avg_transaction = df['transaction_amount'].mean()
        high_value_failure = df[df['transaction_amount'] > avg_transaction * 3]['is_failed'].mean()
        
        if high_value_failure > failure_rate * 1.5:
            insights.append({
                'type': 'insight',
                'title': 'High-Value Transaction Risk',
                'content': f'Large transactions (>${avg_transaction*3:.2f}) have {high_value_failure*100:.1f}% failure rate, significantly higher than average.',
                'recommendation': 'Implement special handling for high-value transactions with dedicated processing queues.'
            })
        
        # Weekend vs weekday patterns
        df['is_weekend'] = df['day_of_week'].isin([5, 6])
        weekend_failure = df[df['is_weekend']]['is_failed'].mean()
        weekday_failure = df[~df['is_weekend']]['is_failed'].mean()
        
        if abs(weekend_failure - weekday_failure) > 0.05:
            insights.append({
                'type': 'insight',
                'title': 'Weekend Pattern Detected',
                'content': f'Weekend failure rate ({weekend_failure*100:.1f}%) differs from weekday rate ({weekday_failure*100:.1f}%).',
                'recommendation': 'Adjust staffing and monitoring based on day-of-week patterns.'
            })
        
        # Recent trend
        recent_data = df.sort_values('transaction_date').tail(int(len(df) * 0.1))
        old_data = df.sort_values('transaction_date').head(int(len(df) * 0.1))
        
        recent_failure = recent_data['is_failed'].mean()
        old_failure = old_data['is_failed'].mean()
        
        if recent_failure < old_failure * 0.8:
            insights.append({
                'type': 'insight',
                'title': 'Improving Trend',
                'content': f'Recent failure rate ({recent_failure*100:.1f}%) shows significant improvement from earlier period ({old_failure*100:.1f}%).',
                'recommendation': 'Continue current optimization strategies and monitor for sustained improvement.'
            })
        elif recent_failure > old_failure * 1.2:
            insights.append({
                'type': 'warning',
                'title': 'Deteriorating Performance',
                'content': f'Recent failure rate ({recent_failure*100:.1f}%) has increased from earlier period ({old_failure*100:.1f}%).',
                'recommendation': 'Investigate recent changes and implement emergency response measures.'
            })
        
        return insights
    
    def _prepare_context(self):
        """Prepare context for AI analysis"""
        metrics = {
            'total_transactions': len(self.df),
            'failure_rate': self.df['is_failed'].mean() * 100,
            'total_amount': self.df['transaction_amount'].sum(),
            'failed_amount': self.df[self.df['is_failed']]['transaction_amount'].sum(),
            'branches': self.df['branch_name'].nunique(),
            'date_range': f"{self.df['transaction_date'].min()} to {self.df['transaction_date'].max()}"
        }
        
        context = f"""
        Transaction Data Summary:
        - Total Transactions: {metrics['total_transactions']:,}
        - Overall Failure Rate: {metrics['failure_rate']:.2f}%
        - Total Transaction Amount: ${metrics['total_amount']:,.2f}
        - Failed Transaction Amount: ${metrics['failed_amount']:,.2f}
        - Number of Branches: {metrics['branches']}
        - Date Range: {metrics['date_range']}
        """
        
        return context