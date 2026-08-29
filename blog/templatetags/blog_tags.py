import markdown
import nh3
from pymdownx.emoji import gemoji, to_alt
from copy import deepcopy
from django.utils.safestring import mark_safe
from django import template
from django.db.models import Count

from ..models import Post

register = template.Library()


@register.filter(name='markdown')
def markdown_format(text):
    html = markdown.markdown(
        text,
        extensions=[
            'fenced_code',
            'nl2br',
            'pymdownx.emoji',
        ],
        extension_configs={
            'pymdownx.emoji': {
               'emoji_index': gemoji,
               'emoji_generator': to_alt,
            }
        }
    )
    
    attrs = deepcopy(nh3.ALLOWED_ATTRIBUTES)
    attrs.setdefault('code', set()).add('class')
    
    safe_html = nh3.clean(html, attributes=attrs)
    return mark_safe(safe_html)

@register.simple_tag
def total_posts():
    return Post.published.count()

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}

@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(
        total_comments=Count('comments')
    ).exclude(total_comments=0).order_by('-total_comments')[:count]

