
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from pagination.models import Article  

class Command(BaseCommand):
    help = 'Generate sample articles for pagination testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of articles to create (default: 50)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing articles before creating new ones',
        )
        parser.add_argument(
            '--published-ratio',
            type=float,
            default=0.8,
            help='Ratio of published articles (0.0 to 1.0, default: 0.8)',
        )
    
    def handle(self, *args, **options):
        count = options['count']
        clear_existing = options['clear']
        published_ratio = options['published_ratio']
        
        # Validate published ratio
        if not 0.0 <= published_ratio <= 1.0:
            self.stdout.write(
                self.style.ERROR('Published ratio must be between 0.0 and 1.0')
            )
            return
        
        # Sample data
        authors = [
            'John Smith', 'Jane Doe', 'Alice Johnson', 'Bob Wilson',
            'Carol Brown', 'David Lee', 'Emma Davis', 'Frank Miller',
            'Grace Taylor', 'Henry Anderson', 'Ivy Martinez', 'Jack Thompson'
        ]
        
        topics = [
            'Technology', 'Science', 'Health', 'Sports', 'Travel',
            'Food', 'Education', 'Environment', 'Art', 'Music',
            'Business', 'Politics', 'History', 'Literature', 'Philosophy'
        ]
        
        content_templates = [
            """This comprehensive article explores the fascinating world of {topic}. 
            
Recent developments in {topic} have shown remarkable progress, with experts noting significant improvements across multiple areas. The implications of these advances are far-reaching and promise to reshape our understanding of the field.

Key highlights include:
• Revolutionary approaches to traditional problems
• Innovative methodologies and techniques  
• Emerging trends that will define the future
• Expert insights from leading professionals

Through careful analysis and research, this article provides readers with valuable perspectives on current challenges and opportunities in {topic}. The findings presented here offer actionable insights for both newcomers and seasoned professionals.

As we look toward the future, it's clear that {topic} will continue to evolve rapidly, presenting both exciting possibilities and unique challenges for practitioners and enthusiasts alike.""",

            """In this detailed exploration of {topic}, we delve deep into the current landscape and emerging trends that are shaping the industry.

The world of {topic} has undergone significant transformation in recent years, driven by technological advancement and changing consumer demands. This evolution has created new opportunities while also presenting unique challenges that require innovative solutions.

Our analysis covers:
- Historical context and evolution
- Current market dynamics  
- Technological innovations
- Future predictions and trends
- Practical applications

Expert {author} brings years of experience to this discussion, offering unique insights that bridge theory and practice. The recommendations provided here are based on extensive research and real-world implementation.

Whether you're a beginner or an experienced professional in {topic}, this article provides valuable information to help you navigate the complex landscape and make informed decisions.""",

            """This in-depth article examines the critical aspects of {topic} that every professional should understand.

{Topic} continues to be a rapidly evolving field, with new discoveries and innovations emerging regularly. Understanding these developments is crucial for anyone looking to stay current with industry best practices and emerging opportunities.

The article addresses several key areas:
1. Fundamental principles and concepts
2. Recent breakthrough developments
3. Practical implementation strategies
4. Common challenges and solutions
5. Future outlook and predictions

Author {author} combines theoretical knowledge with practical experience to provide readers with a comprehensive overview that is both informative and actionable. The insights shared here reflect current industry standards and forward-thinking approaches.

This analysis will prove valuable for decision-makers, practitioners, and anyone interested in gaining a deeper understanding of {topic} and its implications for the future."""
        ]
        
        # Clear existing articles if requested
        if clear_existing:
            deleted_count = Article.objects.count()
            Article.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing articles')
            )
        
        # Generate articles
        articles_to_create = []
        
        self.stdout.write(f'Generating {count} articles...')
        
        for i in range(count):
            topic = random.choice(topics)
            author = random.choice(authors)
            content_template = random.choice(content_templates)
            
            # Determine if this article should be published
            is_published = random.random() < published_ratio
            
            # Create varied and realistic titles
            title_formats = [
                f"Understanding {topic}: A Comprehensive Guide",
                f"The Future of {topic}: Trends and Predictions", 
                f"{topic} Best Practices for {random.randint(2024, 2025)}",
                f"Advanced Techniques in {topic}",
                f"Mastering {topic}: Expert Insights",
                f"The Complete {topic} Handbook",
                f"{topic} Innovations and Breakthroughs",
                f"Essential {topic} Strategies",
                f"{topic}: From Theory to Practice",
                f"Modern Approaches to {topic}"
            ]
            
            title = random.choice(title_formats)
            
            # Format content with topic and author
            content = content_template.format(
                topic=topic.lower(),
                Topic=topic,
                author=author
            ).strip()
            
            article = Article(
                title=title,
                content=content,
                author=author,
                is_published=is_published
            )
            articles_to_create.append(article)
            
            # Show progress for large batches
            if (i + 1) % 10 == 0:
                self.stdout.write(f'  Generated {i + 1}/{count} articles...')
        
        # Bulk create for better performance
        try:
            Article.objects.bulk_create(articles_to_create, batch_size=100)
            
            # Get final counts
            total_count = Article.objects.count()
            published_count = Article.objects.filter(is_published=True).count()
            unpublished_count = Article.objects.filter(is_published=False).count()
            
            # Success message
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully created {count} articles!\n'
                    f'Database now contains {total_count} total articles:\n'
                    f'  • Published: {published_count} articles\n'
                    f'  • Unpublished: {unpublished_count} articles\n'
                    f'  • Published ratio: {published_count/total_count:.1%}'
                )
            )
            
            # Show some sample titles
            self.stdout.write('\nSample articles created:')
            sample_articles = Article.objects.filter(is_published=True)[:3]
            for article in sample_articles:
                self.stdout.write(f'  • "{article.title}" by {article.author}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating articles: {str(e)}')
            )
            return
        
        # Provide usage instructions
        self.stdout.write(
            self.style.SUCCESS(
                f'\nArticles are ready for pagination testing!'
                f'\nYou can now test your API at /api/articles/'
            )
        )