from datetime import datetime, timedelta
from database import db
from models.vehicle import Vehicle
from models.customer import Customer
from models.reminder import Reminder
from models.job_sheet import JobSheet
from sqlalchemy import func, and_, or_


class AIInsightsService:
    """Service for generating AI-powered insights based on real data"""
    
    def __init__(self):
        self.today = datetime.now().date()
    
    def generate_insights(self):
        """Generate comprehensive AI insights based on current data"""
        insights = []
        
        # Get basic data counts
        total_vehicles = Vehicle.query.count()
        total_customers = Customer.query.count()
        total_reminders = Reminder.query.count()
        total_job_sheets = JobSheet.query.count()
        
        if total_vehicles == 0:
            return [{
                'type': 'info',
                'icon': '💡',
                'title': 'Getting Started',
                'message': 'Upload your vehicle data or job sheets to start receiving AI-powered insights and recommendations.'
            }]
        
        # Generate MOT-related insights
        insights.extend(self._generate_mot_insights())
        
        # Generate customer insights
        insights.extend(self._generate_customer_insights())
        
        # Generate business insights
        insights.extend(self._generate_business_insights())
        
        # Generate operational insights
        insights.extend(self._generate_operational_insights())
        
        # Limit to top 3 most important insights
        return insights[:3]
    
    def _generate_mot_insights(self):
        """Generate MOT-related insights"""
        insights = []
        
        # Check for overdue MOTs
        overdue_vehicles = Vehicle.query.filter(
            and_(
                Vehicle.mot_expiry.isnot(None),
                Vehicle.mot_expiry < self.today
            )
        ).count()
        
        if overdue_vehicles > 0:
            insights.append({
                'type': 'urgent',
                'icon': '🚨',
                'title': 'Urgent Action Required',
                'message': f'{overdue_vehicles} vehicle{"s" if overdue_vehicles != 1 else ""} {"have" if overdue_vehicles != 1 else "has"} overdue MOTs. Contact these customers immediately to schedule appointments.'
            })
        
        # Check for MOTs expiring soon
        thirty_days = self.today + timedelta(days=30)
        expiring_soon = Vehicle.query.filter(
            and_(
                Vehicle.mot_expiry.isnot(None),
                Vehicle.mot_expiry >= self.today,
                Vehicle.mot_expiry <= thirty_days
            )
        ).count()
        
        if expiring_soon > 0:
            insights.append({
                'type': 'warning',
                'icon': '⚠️',
                'title': 'MOTs Expiring Soon',
                'message': f'{expiring_soon} vehicle{"s" if expiring_soon != 1 else ""} {"have" if expiring_soon != 1 else "has"} MOTs expiring within 30 days. Start sending reminders to maximize booking rates.'
            })
        
        # Check for vehicles without MOT dates
        no_mot_data = Vehicle.query.filter(Vehicle.mot_expiry.is_(None)).count()
        if no_mot_data > 0:
            total_vehicles = Vehicle.query.count()
            percentage = (no_mot_data / total_vehicles) * 100
            insights.append({
                'type': 'info',
                'icon': '📊',
                'title': 'Data Quality Opportunity',
                'message': f'{no_mot_data} vehicles ({percentage:.1f}%) are missing MOT expiry dates. Complete this data to improve reminder accuracy.'
            })
        
        return insights
    
    def _generate_customer_insights(self):
        """Generate customer-related insights"""
        insights = []
        
        # Check customer linking rate
        total_job_sheets = JobSheet.query.count()
        if total_job_sheets > 0:
            linked_customers = JobSheet.query.filter(JobSheet.linked_customer_id.isnot(None)).count()
            link_rate = (linked_customers / total_job_sheets) * 100
            
            if link_rate < 80:
                insights.append({
                    'type': 'recommendation',
                    'icon': '🔗',
                    'title': 'Customer Linking Opportunity',
                    'message': f'Only {link_rate:.1f}% of job sheets are linked to customers. Improve linking to enable better customer tracking and targeted reminders.'
                })
        
        # Check for repeat customers
        repeat_customers = db.session.query(JobSheet.customer_name).filter(
            JobSheet.customer_name.isnot(None)
        ).group_by(JobSheet.customer_name).having(func.count(JobSheet.id) > 1).count()
        
        if repeat_customers > 0:
            insights.append({
                'type': 'success',
                'icon': '🎯',
                'title': 'Customer Loyalty Detected',
                'message': f'{repeat_customers} customers have multiple job records. These loyal customers are prime candidates for proactive MOT reminders.'
            })
        
        return insights
    
    def _generate_business_insights(self):
        """Generate business performance insights"""
        insights = []
        
        # Analyze recent job trends
        thirty_days_ago = self.today - timedelta(days=30)
        recent_jobs = JobSheet.query.filter(
            JobSheet.date_created >= thirty_days_ago
        ).count()
        
        if recent_jobs > 0:
            # Calculate average revenue
            recent_revenue = db.session.query(func.sum(JobSheet.grand_total)).filter(
                and_(
                    JobSheet.date_created >= thirty_days_ago,
                    JobSheet.grand_total.isnot(None)
                )
            ).scalar() or 0
            
            if recent_revenue > 0:
                avg_job_value = recent_revenue / recent_jobs
                insights.append({
                    'type': 'info',
                    'icon': '💰',
                    'title': 'Revenue Insight',
                    'message': f'Average job value in the last 30 days: £{avg_job_value:.2f}. Focus on high-value services to maximize revenue per customer.'
                })
        
        return insights
    
    def _generate_operational_insights(self):
        """Generate operational efficiency insights"""
        insights = []
        
        # Check reminder efficiency
        scheduled_reminders = Reminder.query.filter_by(status='scheduled').count()
        sent_reminders = Reminder.query.filter_by(status='sent').count()
        
        if scheduled_reminders > 10:
            insights.append({
                'type': 'action',
                'icon': '📤',
                'title': 'Reminder Backlog',
                'message': f'{scheduled_reminders} reminders are scheduled but not yet sent. Process these to maintain customer engagement.'
            })
        
        # Check for seasonal patterns
        current_month = self.today.month
        if current_month in [2, 3, 8, 9]:  # Peak MOT months
            insights.append({
                'type': 'prediction',
                'icon': '📈',
                'title': 'Seasonal Trend Alert',
                'message': 'Historical data shows increased MOT demand during this period. Consider extending operating hours or booking additional staff.'
            })
        
        return insights
    
    def get_quick_stats(self):
        """Get quick statistics for the dashboard"""
        overdue_count = Vehicle.query.filter(
            and_(
                Vehicle.mot_expiry.isnot(None),
                Vehicle.mot_expiry < self.today
            )
        ).count()
        
        thirty_days = self.today + timedelta(days=30)
        expiring_soon_count = Vehicle.query.filter(
            and_(
                Vehicle.mot_expiry.isnot(None),
                Vehicle.mot_expiry >= self.today,
                Vehicle.mot_expiry <= thirty_days
            )
        ).count()
        
        total_vehicles = Vehicle.query.count()
        pending_reminders = Reminder.query.filter_by(status='scheduled').count()
        
        return {
            'overdue_mots': overdue_count,
            'expiring_soon': expiring_soon_count,
            'total_vehicles': total_vehicles,
            'pending_reminders': pending_reminders
        }
