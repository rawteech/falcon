from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.views.generic import ListView
from django.db.models import Count

from blog.models import Post, Comments
from blog.forms import EmailPostForm, CommentForm, SearchForm

from decouple import config
from taggit.models import Tag
from haystack.query import SearchQuerySet


def post_list(request, tag_slug=None):
	object_list = Post.published.all()
	tag = None

	if tag_slug:
		tag = get_object_or_404(Tag, slug=tag_slug)
		object_list = object_list.filter(tags__in=[tag])

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
		'tag': tag,
	}
	return render(request, 'blog/post/list.html', context)


def post_detail(request, year, month, day, post):
	post = get_object_or_404(Post, slug=post,
								   status='published',
								   publish__year=year,
								   publish__month=month,
								   publish__day=day)
	# Display active comments
	comments = post.comments.filter(active=True)

	if request.method == 'POST':
		# Meaning a comment was posted
		comment_form = CommentForm(data=request.POST)

		if comment_form.is_valid():
			# Create comment object but dont save it yet
			new_comment = comment_form.save(commit=False)

			# Assign current post to the comment
			new_comment.post = post

			# Now save the comment
			new_comment.save()
	else:
		comment_form = CommentForm()

	post_tags_ids = post.tags.values_list('id', flat=True)
	similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
	similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

	context = {
		'post': post, 
		'comments': comments, 
		'comment_form': comment_form,
		'similar_posts': similar_posts,
	}
	return render(request, 'blog/post/detail.html', context)


def post_share(request, post_id):
	# Retrieving post by id
	post = get_object_or_404(Post, id=post_id, status='published')
	sent = False

	if request.method == 'POST':
		# Meaning form was submitted
		form = EmailPostForm(request.POST)
		if form.is_valid():
			# Validation passed
			cd = form.cleaned_data
			
			post_url = request.build_absolute_uri(post.get_absolute_url())
			subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
			message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
			send_mail(subject, message, config('EMAIL_HOST_USER'), [cd['to']])
			sent = True
	else:
		form = EmailPostForm()

	context = {
		'post': post, 
		'form': form, 
		'sent': sent,
	}
	return render(request, 'blog/post/share.html', context)


def post_search(request):
	form = SearchForm()
	context = dict()

	if 'query' in request.GET:
		form = SearchForm(request.GET)
		
		# form validation
		if form.is_valid():
			cd = form.cleaned_data
			results = SearchQuerySet().models(Post).filter(content=cd['query']).load_all()

			# count total results
			total_results = results.count()

			context['cd'] = cd
			context['results'] = results
			context['total_results'] = total_results

	context['form'] = form
	return render(request, 'blog/post/search.html', context)

# class PostListView(ListView):
# 	queryset = Post.published.all()
# 	context_object_name = 'posts'
# 	paginate_by = 3
# 	template_name = 'blog/post/list.html'
