# gamification.py
import pandas as pd
import numpy as np

class BranchGamification:
    def __init__(self, df):
        self.df = df
        self._initialize_scores()
    
    def _initialize_scores(self):
        """Initialize gamification scores for each branch"""
        branch_metrics = self.df.groupby('branch_name').agg({
            'is_failed': 'mean',
            'transaction_amount': 'sum',
            'transaction_date': 'count'
        }).rename(columns={
            'is_failed': 'failure_rate',
            'transaction_amount': 'total_amount',
            'transaction_date': 'transaction_count'
        })
        
        # Calculate points based on performance
        branch_metrics['performance_score'] = (1 - branch_metrics['failure_rate']) * 100
        branch_metrics['volume_score'] = branch_metrics['transaction_count'] / branch_metrics['transaction_count'].max() * 100
        branch_metrics['revenue_score'] = branch_metrics['total_amount'] / branch_metrics['total_amount'].max() * 100
        
        # Total points
        branch_metrics['total_points'] = (
            branch_metrics['performance_score'] * 0.5 +
            branch_metrics['volume_score'] * 0.3 +
            branch_metrics['revenue_score'] * 0.2
        ) * 10  # Scale up for bigger numbers
        
        self.scores = branch_metrics
    
    def get_leaderboard(self):
        """Get the current leaderboard"""
        leaderboard = self.scores.sort_values('total_points', ascending=False).copy()
        leaderboard = leaderboard.reset_index()
        leaderboard['rank'] = range(1, len(leaderboard) + 1)
        
        # Add rank emojis
        rank_emojis = {1: '🥇', 2: '🥈', 3: '🥉'}
        leaderboard['rank_display'] = leaderboard['rank'].apply(lambda x: rank_emojis.get(x, f'#{x}'))
        
        return leaderboard[['rank_display', 'branch_name', 'total_points', 'performance_score', 'failure_rate']]
    
    def get_branch_details(self, branch_name):
        """Get detailed statistics for a specific branch"""
        branch_data = self.scores.loc[branch_name]
        
        # Calculate level based on points
        level = int(branch_data['total_points'] / 500) + 1
        
        # Calculate streak (simplified - based on recent performance)
        branch_df = self.df[self.df['branch_name'] == branch_name]
        recent_data = branch_df.sort_values('transaction_date').tail(100)
        recent_failure_rate = recent_data['is_failed'].mean()
        streak = 7 if recent_failure_rate < 0.05 else 3 if recent_failure_rate < 0.10 else 1
        
        return {
            'level': level,
            'total_points': int(branch_data['total_points']),
            'current_streak': streak,
            'failure_rate': branch_data['failure_rate'],
            'performance_score': branch_data['performance_score'],
            'achievement_count': np.random.randint(3, 15)  # Placeholder
        }
    
    def check_achievements(self, branch_name):
        """Check achievements for a branch"""
        branch_data = self.scores.loc[branch_name]
        achievements = []
        
        # Performance achievements
        if branch_data['failure_rate'] < 0.05:
            achievements.append({
                'name': 'Zero Defect Hero',
                'description': 'Maintained failure rate below 5%',
                'badge': '🏆',
                'points': 500
            })
        
        if branch_data['failure_rate'] < 0.10:
            achievements.append({
                'name': 'Reliability Champion',
                'description': 'Maintained failure rate below 10%',
                'badge': '🥇',
                'points': 300
            })
        
        # Volume achievements
        if branch_data['transaction_count'] > self.scores['transaction_count'].quantile(0.9):
            achievements.append({
                'name': 'High Volume Master',
                'description': 'Processed transactions in top 10%',
                'badge': '🚀',
                'points': 400
            })
        
        # Revenue achievements
        if branch_data['total_amount'] > self.scores['total_amount'].quantile(0.9):
            achievements.append({
                'name': 'Revenue Leader',
                'description': 'Generated revenue in top 10%',
                'badge': '💰',
                'points': 400
            })
        
        return achievements