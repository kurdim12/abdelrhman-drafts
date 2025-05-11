from ai_agent import FinancialAnalysisAgent
from advanced_features import PredictiveFailurePreventor, SmartTransactionRouter, AnomalyDNASystem
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go

class SuperFinancialAgent(FinancialAnalysisAgent):
    def __init__(self, df):
        super().__init__(df)
        self.pfp = PredictiveFailurePreventor(df)
        self.router = SmartTransactionRouter(df)
        self.dna = AnomalyDNASystem(df)
    
    def analyze_with_prediction(self, question):
        """Enhanced analysis with predictive capabilities"""
        # Get standard analysis
        standard_result = self.query(question)
        
        # Add predictive insights if relevant
        if any(keyword in question.lower() for keyword in ['failure', 'risk', 'predict', 'future']):
            pfp_insights = self._generate_pfp_insights()
            standard_result['response'] += f"\n\n**Predictive Analysis:**\n{pfp_insights}"
        
        # Add routing recommendations if relevant
        if any(keyword in question.lower() for keyword in ['route', 'gateway', 'process']):
            routing_insights = self._generate_routing_insights()
            standard_result['response'] += f"\n\n**Smart Routing Recommendations:**\n{routing_insights}"
        
        return standard_result
    
    def find_patterns(self, df):
        """Find patterns in transaction data"""
        patterns = []
        
        # Time-based patterns
        hourly_pattern = df.groupby('hour')['is_failed'].mean()
        peak_hours = hourly_pattern.nlargest(3).index.tolist()
        low_hours = hourly_pattern.nsmallest(3).index.tolist()
        
        patterns.append({
            'name': 'Peak Failure Hours',
            'description': f'Highest failure rates occur at hours: {", ".join(map(str, peak_hours))} with rates around {hourly_pattern[peak_hours].mean():.1%}',
            'impact': 'High',
            'visual': self._create_hourly_pattern_chart(hourly_pattern)
        })
        
        patterns.append({
            'name': 'Low Risk Hours',
            'description': f'Lowest failure rates occur at hours: {", ".join(map(str, low_hours))} with rates around {hourly_pattern[low_hours].mean():.1%}',
            'impact': 'Medium',
            'visual': None
        })
        
        # Branch patterns
        branch_pattern = df.groupby('branch_name')['is_failed'].mean()
        high_risk_branches = branch_pattern.nlargest(3).index.tolist()
        
        patterns.append({
            'name': 'High-Risk Branches',
            'description': f'Branches with highest failure rates: {", ".join(high_risk_branches)} with average rate of {branch_pattern[high_risk_branches].mean():.1%}',
            'impact': 'High',
            'visual': self._create_branch_pattern_chart(branch_pattern)
        })
        
        # Amount-based patterns
        high_amount_data = df[df['transaction_amount'] > df['transaction_amount'].quantile(0.9)]
        high_amount_failure = high_amount_data['is_failed'].mean()
        
        patterns.append({
            'name': 'High-Value Transaction Risk',
            'description': f'Transactions above ${df["transaction_amount"].quantile(0.9):.2f} have a {high_amount_failure:.1%} failure rate',
            'impact': 'Medium' if high_amount_failure < 0.2 else 'High',
            'visual': None
        })
        
        # Weekly patterns
        daily_pattern = df.groupby('day_of_week')['is_failed'].mean()
        weekend_rate = daily_pattern[[5, 6]].mean()  # Saturday and Sunday
        weekday_rate = daily_pattern[[0, 1, 2, 3, 4]].mean()  # Monday to Friday
        
        if abs(weekend_rate - weekday_rate) > 0.05:
            patterns.append({
                'name': 'Weekend vs Weekday Pattern',
                'description': f'Weekend failure rate ({weekend_rate:.1%}) differs significantly from weekday rate ({weekday_rate:.1%})',
                'impact': 'Medium',
                'visual': self._create_weekly_pattern_chart(daily_pattern)
            })
        
        return patterns
    
    def analyze_root_causes(self, df):
        """Analyze root causes of failures"""
        causes = []
        
        # Time-based analysis
        hourly_failure = df.groupby('hour')['is_failed'].mean()
        peak_hours = hourly_failure.nlargest(3).index.tolist()
        
        causes.append({
            'factor': 'Peak Hour Congestion',
            'impact': f'Hours {", ".join(map(str, peak_hours))} show {hourly_failure[peak_hours].mean():.1%} failure rate',
            'recommendation': 'Scale infrastructure during peak hours or implement load balancing'
        })
        
        # Branch analysis
        branch_failure = df.groupby('branch_name')['is_failed'].mean()
        high_fail_branches = branch_failure[branch_failure > branch_failure.mean() + branch_failure.std()].index.tolist()
        
        if high_fail_branches:
            causes.append({
                'factor': 'Branch-Specific Issues',
                'impact': f'Branches {", ".join(high_fail_branches)} have significantly higher failure rates',
                'recommendation': 'Investigate branch-specific infrastructure or process issues'
            })
        
        # Amount analysis
        amount_bins = pd.qcut(df['transaction_amount'], q=5, duplicates='drop')
        amount_failure = df.groupby(amount_bins)['is_failed'].mean()
        
        if amount_failure.iloc[-1] > amount_failure.mean() * 1.5:
            causes.append({
                'factor': 'High-Value Transaction Processing',
                'impact': f'Large transactions (>${df["transaction_amount"].quantile(0.8):.2f}) fail {amount_failure.iloc[-1]:.1%} of the time',
                'recommendation': 'Implement special handling for high-value transactions'
            })
        
        # System load analysis
        transaction_volume = df.groupby('hour').size()
        failure_correlation = transaction_volume.corr(hourly_failure)
        
        if failure_correlation > 0.5:
            causes.append({
                'factor': 'System Load Correlation',
                'impact': f'Strong correlation ({failure_correlation:.2f}) between transaction volume and failures',
                'recommendation': 'Implement auto-scaling based on transaction volume'
            })
        
        return causes
    
    def generate_optimization_strategy(self, df):
        """Generate optimization strategy based on analysis"""
        strategy = []
        
        # Analyze current state
        metrics = {
            'failure_rate': df['is_failed'].mean(),
            'peak_hour_failure': df.groupby('hour')['is_failed'].mean().max(),
            'branch_variance': df.groupby('branch_name')['is_failed'].mean().std(),
            'high_amount_failure': df[df['transaction_amount'] > df['transaction_amount'].quantile(0.9)]['is_failed'].mean()
        }
        
        # Priority 1: Address immediate issues
        if metrics['failure_rate'] > 0.15:
            strategy.append({
                'priority': 1,
                'action': 'Implement Emergency Failure Reduction Protocol',
                'expected_outcome': f'Reduce overall failure rate from {metrics["failure_rate"]:.1%} to below 10%',
                'difficulty': 'Medium',
                'timeline': '1-2 weeks',
                'steps': [
                    'Deploy auto-retry mechanism for failed transactions',
                    'Implement circuit breaker pattern',
                    'Add redundant payment gateways'
                ]
            })
        
        # Priority 2: Peak hour optimization
        if metrics['peak_hour_failure'] > 0.20:
            strategy.append({
                'priority': 2,
                'action': 'Optimize Peak Hour Performance',
                'expected_outcome': f'Reduce peak hour failures from {metrics["peak_hour_failure"]:.1%} to below 15%',
                'difficulty': 'High',
                'timeline': '2-4 weeks',
                'steps': [
                    'Implement dynamic scaling during peak hours',
                    'Add caching layer for frequent operations',
                    'Optimize database queries and indexes'
                ]
            })
        
        # Priority 3: Branch standardization
        if metrics['branch_variance'] > 0.05:
            strategy.append({
                'priority': 3,
                'action': 'Standardize Branch Performance',
                'expected_outcome': f'Reduce performance variance between branches from {metrics["branch_variance"]:.1%} to below 3%',
                'difficulty': 'Medium',
                'timeline': '3-6 weeks',
                'steps': [
                    'Audit underperforming branches',
                    'Standardize infrastructure across all branches',
                    'Implement best practices from top-performing branches'
                ]
            })
        
        # Priority 4: High-value transaction handling
        if metrics['high_amount_failure'] > 0.10:
            strategy.append({
                'priority': 4,
                'action': 'Enhance High-Value Transaction Processing',
                'expected_outcome': f'Reduce high-value transaction failures from {metrics["high_amount_failure"]:.1%} to below 5%',
                'difficulty': 'Low',
                'timeline': '1-2 weeks',
                'steps': [
                    'Create dedicated processing queue for high-value transactions',
                    'Implement additional validation checks',
                    'Add manual review option for critical transactions'
                ]
            })
        
        # Priority 5: Long-term improvements
        strategy.append({
            'priority': 5,
            'action': 'Implement Predictive Failure Prevention',
            'expected_outcome': 'Proactively prevent 30-40% of failures before they occur',
            'difficulty': 'High',
            'timeline': '2-3 months',
            'steps': [
                'Deploy machine learning models for failure prediction',
                'Implement real-time monitoring and alerting',
                'Create automated response system for predicted failures'
            ]
        })
        
        return strategy
    
    def _create_hourly_pattern_chart(self, hourly_pattern):
        """Create visualization for hourly pattern"""
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=hourly_pattern.index,
            y=hourly_pattern.values * 100,
            name='Failure Rate'
        ))
        
        fig.update_layout(
            title='Hourly Failure Rate Pattern',
            xaxis_title='Hour of Day',
            yaxis_title='Failure Rate (%)',
            showlegend=False
        )
        
        return fig
    
    def _create_branch_pattern_chart(self, branch_pattern):
        """Create visualization for branch pattern"""
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=branch_pattern.index,
            y=branch_pattern.values * 100,
            name='Failure Rate'
        ))
        
        fig.update_layout(
            title='Branch Failure Rates',
            xaxis_title='Branch',
            yaxis_title='Failure Rate (%)',
            showlegend=False
        )
        
        return fig
    
    def _create_weekly_pattern_chart(self, daily_pattern):
        """Create visualization for weekly pattern"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=days,
            y=daily_pattern.values * 100,
            name='Failure Rate'
        ))
        
        fig.update_layout(
            title='Weekly Failure Rate Pattern',
            xaxis_title='Day of Week',
            yaxis_title='Failure Rate (%)',
            showlegend=False
        )
        
        return fig
    
    def _generate_pfp_insights(self):
        """Generate predictive insights"""
        high_risk_branches = []
        
        for branch in self.df['branch_name'].unique():
            score = self.pfp.calculate_pfp_score({
                'branch': branch,
                'hour': datetime.now().hour,
                'amount': self.df[self.df['branch_name'] == branch]['transaction_amount'].mean()
            })
            
            if score['risk_level'] == 'High':
                high_risk_branches.append((branch, score['score']))
        
        insights = f"Currently {len(high_risk_branches)} branches show high risk patterns.\n"
        if high_risk_branches:
            insights += "High-risk branches: " + ", ".join([f"{b[0]} (Risk Score: {b[1]:.2f})" for b in high_risk_branches[:3]])
            insights += "\n\nRecommended Actions:\n"
            insights += "1. Route transactions through secondary gateways for high-risk branches\n"
            insights += "2. Increase monitoring frequency during peak risk hours\n"
            insights += "3. Consider implementing transaction chunking for large amounts"
        
        return insights
    
    def _generate_routing_insights(self):
        """Generate routing insights"""
        insights = []
        current_hour = datetime.now().hour
        
        for branch in self.df['branch_name'].unique()[:3]:  # Top 3 branches
            routing = self.router.route_transaction(branch, 500, datetime.now())
            insights.append(f"{branch}: Use {routing['gateway']} with {routing['retry_strategy']} retry strategy")
        
        return "\n".join(insights)
    
    def get_real_time_recommendations(self, branch, amount):
        """Get real-time recommendations for a specific transaction"""
        # PFP Score
        pfp_result = self.pfp.calculate_pfp_score({
            'branch': branch,
            'hour': datetime.now().hour,
            'amount': amount
        })
        
        # Routing recommendation
        routing = self.router.route_transaction(branch, amount, datetime.now())
        
        # DNA pattern matching
        current_pattern = {'branch': branch, 'hour': datetime.now().hour}
        dna_matches = self.dna.match_anomaly_pattern(current_pattern)
        
        return {
            'pfp_score': pfp_result,
            'routing': routing,
            'dna_matches': dna_matches,
            'overall_recommendation': self._generate_overall_recommendation(pfp_result, routing, dna_matches)
        }
    
    def _generate_overall_recommendation(self, pfp_result, routing, dna_matches):
        if pfp_result['risk_level'] == 'High':
            return "HIGH RISK: Consider delaying transaction or using enhanced monitoring"
        elif pfp_result['risk_level'] == 'Medium':
            return f"MODERATE RISK: Proceed with {routing['gateway']} and standard monitoring"
        else:
            return "LOW RISK: Transaction can proceed normally"