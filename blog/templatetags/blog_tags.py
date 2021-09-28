from django import template
from django.db.models import Count
from ..models import Post

register = template.Library()

@register.simple_tag
def total_posts():
    return Post.objects.all().count() # Post.published.count()

@register.inclusion_tag('blog/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.objects.all().order_by('-publish')[:count] # Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}

@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.objects.all().annotate(total_comments = Count('comments')).order_by('-total_comments')[:count]