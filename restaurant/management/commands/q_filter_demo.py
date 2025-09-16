# management/commands/q_filter_demo.py
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import json

from restaurant.models import Restaurant, Sale
from restaurant.q_filters import (
    italian_mexican_q,
    recently_opened_q,
    recently_opened,
    last_30_days_q,
    grill_name_q,
    cafe_ending_q,
    name_has_digit_q,
    profitable_q,
    restaurant_name_has_digit_q,
    italian_mexican_or_recent_q,
    profitable_or_digit_name_q
)


class Command(BaseCommand):
    help = 'Demonstrates Q objects, pattern matching, and regex lookups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-sample-data',
            action='store_true',
            help='Create sample data for testing',
        )

    def handle(self, *args, **options):
        self.create_sample_data()
        
        self.stdout.write(self.style.SUCCESS('\n=== Q OBJECTS AND PATTERN MATCHING DEMO ===\n'))
        
        # Clear queries to track SQL
        connection.queries_log.clear()
        
        # 1. Q Object Queries
        self.demonstrate_q_objects()
        
        # 2. Pattern Matching Lookups
        self.demonstrate_pattern_matching()
        
        # 3. Regex Lookups
        self.demonstrate_regex_lookups()
        
        # 4. Complex Combined Queries with Performance Optimization
        self.demonstrate_complex_queries()
        
        self.stdout.write(self.style.SUCCESS('\n=== DEMO COMPLETED ==='))

    def create_sample_data(self):
        """Create sample data for testing"""
        self.stdout.write('Creating sample data...')
        
        # Clear existing data
        Sale.objects.all().delete()
        Restaurant.objects.all().delete()
        
        # Create restaurants with various names and types
        restaurants_data = [
            {'name': 'Mario\'s Italian Kitchen', 'type': 'italian', 'days_ago': 45},
            {'name': 'Taco Bell Express', 'type': 'mexican', 'days_ago': 15},
            {'name': 'The Sports Grill', 'type': 'american', 'days_ago': 120},
            {'name': 'Sunset Cafe', 'type': 'american', 'days_ago': 200},
            {'name': 'Pizza Palace 123', 'type': 'italian', 'days_ago': 10},
            {'name': 'Dragon Wok', 'type': 'chinese', 'days_ago': 80},
            {'name': 'Mumbai Spice House', 'type': 'indian', 'days_ago': 25},
            {'name': 'Burger Grill 24/7', 'type': 'american', 'days_ago': 5},
            {'name': 'Le Petit Cafe', 'type': 'french', 'days_ago': 300},
            {'name': 'Cinco de Mayo Restaurant', 'type': 'mexican', 'days_ago': 60},
        ]
        
        restaurants = []
        for data in restaurants_data:
            opening_date = timezone.now().date() - timedelta(days=data['days_ago'])
            restaurant = Restaurant.objects.create(
                name=data['name'],
                restaurant_type=data['type'],
                date_opened=opening_date
            )
            restaurants.append(restaurant)
        
        # Create sales data
        sales_data = [
            {'income': Decimal('5000.00'), 'expenditure': Decimal('3000.00')},  # Profitable
            {'income': Decimal('2000.00'), 'expenditure': Decimal('2500.00')},  # Loss
            {'income': Decimal('8000.00'), 'expenditure': Decimal('4000.00')},  # Profitable
            {'income': Decimal('1500.00'), 'expenditure': Decimal('1800.00')},  # Loss
            {'income': Decimal('6000.00'), 'expenditure': Decimal('3500.00')},  # Profitable
        ]
        
        for i, restaurant in enumerate(restaurants[:5]):  # Create sales for first 5 restaurants
            Sale.objects.create(
                restaurant=restaurant,
                income=sales_data[i]['income'],
                expenditure=sales_data[i]['expenditure']
            )
        
        # Create additional sales for restaurants with digits in names
        digit_restaurants = [r for r in restaurants if any(c.isdigit() for c in r.name)]
        for restaurant in digit_restaurants:
            Sale.objects.create(
                restaurant=restaurant,
                income=Decimal('3000.00'),
                expenditure=Decimal('4000.00')  # Loss
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(restaurants)} restaurants and {Sale.objects.count()} sales'))

    def demonstrate_q_objects(self):
        """Demonstrate Q object queries"""
        self.stdout.write(self.style.HTTP_INFO('\n1. Q OBJECT QUERIES\n'))
        
        # a. Italian OR Mexican restaurants
        self.stdout.write('a. Restaurants with Italian OR Mexican cuisine:')
        italian_mexican_restaurants = Restaurant.objects.filter(italian_mexican_q)
        self.print_queryset_results(italian_mexican_restaurants, 'Italian/Mexican Restaurants')
        
        # b. Restaurants NOT opened in last 30 days
        self.stdout.write('\nb. Restaurants NOT opened in the last 30 days:')
        not_recent_restaurants = Restaurant.objects.filter(recently_opened_q)
        self.print_queryset_results(not_recent_restaurants, 'Not Recently Opened')
        
        # c. Combined: Italian/Mexican OR opened in last 30 days
        self.stdout.write('\nc. Italian/Mexican OR opened in last 30 days:')
        combined_restaurants = Restaurant.objects.filter(italian_mexican_or_recent_q)
        self.print_queryset_results(combined_restaurants, 'Combined Condition')

    def demonstrate_pattern_matching(self):
        """Demonstrate pattern matching lookups"""
        self.stdout.write(self.style.HTTP_INFO('\n2. PATTERN MATCHING LOOKUPS\n'))
        
        # a. Names containing "grill" (case-insensitive)
        self.stdout.write('a. Restaurants with "grill" in name (case-insensitive):')
        grill_restaurants = Restaurant.objects.filter(grill_name_q)
        self.print_queryset_results(grill_restaurants, 'Grill Restaurants')
        
        # b. Names ending with "Cafe"
        self.stdout.write('\nb. Restaurants ending with "Cafe":')
        cafe_restaurants = Restaurant.objects.filter(cafe_ending_q)
        self.print_queryset_results(cafe_restaurants, 'Cafe Restaurants')

    def demonstrate_regex_lookups(self):
        """Demonstrate regex lookups"""
        self.stdout.write(self.style.HTTP_INFO('\n3. REGEX LOOKUPS\n'))
        
        # a. Names containing one or more digits
        self.stdout.write('a. Restaurants with digits in name:')
        digit_restaurants = Restaurant.objects.filter(name_has_digit_q)
        self.print_queryset_results(digit_restaurants, 'Restaurants with Digits')
        
        # b. Sales where income > expenditure OR restaurant name has digits
        self.stdout.write('\nb. Profitable sales OR restaurant name has digits:')
        complex_sales = Sale.objects.select_related('restaurant').filter(
            profitable_or_digit_name_q
        )
        self.print_sales_results(complex_sales, 'Complex Sales Query')

    def demonstrate_complex_queries(self):
        """Demonstrate complex combined queries with performance optimization"""
        self.stdout.write(self.style.HTTP_INFO('\n4. COMPLEX COMBINED QUERIES WITH OPTIMIZATION\n'))
        
        # Complex query: Sales from (Italian/Mexican OR recently opened) restaurants
        # with select_related for performance
        self.stdout.write('Complex query with select_related optimization:')
        
        complex_q = Sale.objects.select_related('restaurant').filter(
            restaurant__restaurant_type__in=['italian', 'mexican']
        ) | Sale.objects.select_related('restaurant').filter(
            recently_opened
        )
        
        self.print_sales_results(complex_q.distinct(), 'Complex Optimized Query')
        
        # Show the difference without select_related
        self.stdout.write('\nSame query WITHOUT select_related (less efficient):')
        connection.queries_log.clear()
        
        inefficient_q = Sale.objects.filter(
            restaurant__restaurant_type__in=['italian', 'mexican']
        ) | Sale.objects.filter(
            recently_opened
        )
        
        self.print_sales_results(inefficient_q.distinct(), 'Inefficient Query')

    def print_queryset_results(self, queryset, title):
        """Print queryset results and SQL"""
        initial_query_count = len(connection.queries)
        
        results = list(queryset)  # Force evaluation
        
        self.stdout.write(f'\n--- {title} ---')
        self.stdout.write(f'Count: {len(results)}')
        
        for restaurant in results:
            self.stdout.write(f'  • {restaurant.name} ({restaurant.get_restaurant_type_display()}) - Opened: {restaurant.date_opened}')
        
        # Show SQL
        new_queries = connection.queries[initial_query_count:]
        if new_queries:
            self.stdout.write(f'\nSQL Generated:')
            for query in new_queries:
                self.stdout.write(f'  {query["sql"]}')
        
        self.stdout.write('')

    def print_sales_results(self, queryset, title):
        """Print sales queryset results and SQL"""
        initial_query_count = len(connection.queries)
        
        results = list(queryset)  # Force evaluation
        
        self.stdout.write(f'\n--- {title} ---')
        self.stdout.write(f'Count: {len(results)}')
        
        for sale in results:
            profit_status = "Profit" if sale.income > sale.expenditure else "Loss"
            self.stdout.write(
                f'  • {sale.restaurant.name}: Income ${sale.income}, '
                f'Expenditure ${sale.expenditure} ({profit_status})'
            )
        
        # Show SQL
        new_queries = connection.queries[initial_query_count:]
        if new_queries:
            self.stdout.write(f'\nSQL Generated ({len(new_queries)} queries):')
            for i, query in enumerate(new_queries, 1):
                self.stdout.write(f'  Query {i}: {query["sql"]}')
        
        self.stdout.write('')