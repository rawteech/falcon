from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView

from blog.models import Post
from blog.forms import EmailPostForm


# def post_list(request):
# 	object_list = Post.published.all()
# 	paginator = Paginator(object_list, 3)
# 	page = request.GET.get('page')
	
# 	try:
# 		posts = paginator.page(page)
# 	except PageNotAnInteger:
# 		# If page is not an integer, render the first page
# 		posts = paginator.page(1)
# 	except EmptyPage:
# 		# If page is out of range, deliver the last page
# 		posts = paginator.page(paginator.num_pages)
# 	context = {
# 		'page': page,
# 		'posts': posts,
# 	}
# 	return render(request, 'blog/post/list.html', context)


def post_detail(request, year, month, day, post):
	post = get_object_or_404(Post, slug=post,
								   status='published',
								   publish__year=year,
								   publish__month=month,
								   publish__day=day)
	context = {'post': post}
	return render(request, 'blog/post/detail.html', context)


def post_share(request, post_id):
	# Retrieving post by id
	post = get_object_or_404(Post, id=post_id, status='published')

	if request.method == 'POST':
		# Meaning form was submitted
		form = EmailPostForm(request.post)
		if form.is_valid():
			# Validation passed
			cd = form.cleaned_data
	else:
		form = EmailPostForm()

	context = {'post': post, 'form': form}
	return render(request, 'blog/post/share.html', context)


class PostListView(ListView):
	queryset = Post.published.all()
	context_object_name = 'posts'
	paginate_by = 3
	template_name = 'blog/post/list.html'
