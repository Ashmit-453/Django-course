from django.db.models import Q,F
from django.utils import timezone
from datetime import timedelta



italian_mexican_q = Q(restaurant_type='italian') | Q(restaurant_type='mexican')

recently_opened_q = ~Q(date_opened__gte=timezone.now().date() - timedelta(days=30))

last_30_days_q = Q(date_opened__gte=timezone.now().date() - timedelta(days=30))

recently_opened = Q(restaurant__date_opened__gte=timezone.now().date() - timedelta(days=30))

grill_name_q = Q(name__icontains='grill')

cafe_ending_q = Q(name__endswith='Cafe')

name_has_digit_q = Q(name__regex=r'[0-9]+')

profitable_q = Q(income__gt=F('expenditure'))

restaurant_name_has_digit_q = Q(restaurant__name__regex=r'[0-9]+')

italian_mexican_or_recent_q = italian_mexican_q | last_30_days_q
profitable_or_digit_name_q = profitable_q | restaurant_name_has_digit_q