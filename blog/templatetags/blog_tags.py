from django import template

register = template.Library()

from blog.models import Post

@register.simple_tag
def total_posts():
	return Post.published.count()