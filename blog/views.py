from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from blog.models import Post


def post_list(request):
	object_list = Post.published.all()
	paginator = Paginator(object_list, 3)
	page = request.GET.get('page')
	
	try:
		posts = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, render the first page
		posts = paginator.page(1)
	except EmptyPage:
		# If page is out of range, deliver the last page
		posts = paginator.page(paginator.num_pages)
	context = {
		'page': page,
		'posts': posts,
	}
	return render(request, 'blog/post/list.html', context)


def post_detail(request, year, month, day, post):
	post = get_object_or_404(Post, slug=post,
								   status='published',
								   publish__year=year,
								   publish__month=month,
								   publish__day=day)
	context = {'post': post}
	return render(request, 'blog/post/detail.html', context)
