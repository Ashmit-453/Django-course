from rest_framework import viewsets,status
from .serializers import ArticleSerializer
from .models import Article
from rest_framework.response import Response
from django.core.paginator import EmptyPage, PageNotAnInteger
from .pagination import CustomArticlePagination

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = ArticleSerializer
    pagination_class = CustomArticlePagination
    
    def get_queryset(self):
        return Article.objects.filter(is_published=True).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except (EmptyPage, PageNotAnInteger):
            return Response(
                {
                    'error': 'Invalid page number',
                    'detail': 'Page number out of range or not a valid integer'
                },
                status=status.HTTP_404_NOT_FOUND
            )
