from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from .models import Post
from .forms import EmailPostForm, CommentForm

# Create your views here.
def post_list(request, tag_slug=None):
    object__list = Post.objects.all()

    # Tagging Configurations
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object__list = object__list.filter(tags__in=[tag])
    
    # Pagination Configurations
    paginator = Paginator(object__list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request,'blog/list.html', {'posts': posts, 'page': page, 'tag': tag})



def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug = post, status = 'draft', publish__year = year, publish__month = month, publish__day = day)
    
    #List of active comments
    comments = post.comments.filter(active=True)
    new_comment = None

    # Comment form
    if request.method == "POST":
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False) # Create Comment Objet but don't save to database
            new_comment.post = post #Assign the post to new comment
            new_comment.save() # Save the comment to database
        
    else:
        comment_form = CommentForm()

    #Retrieving Posts by SIMILARITY
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.all().filter(tags__in=post_tags_ids).exclude(id=post.id) # Post.published.filter instead of objects.all()filter 
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags',)[:4] # inter the '-published' order

    return render(request, 'blog/detail.html', {'post': post, 'comments':comments, 'new_comment':new_comment, 'comment_form': comment_form, "similar_posts": similar_posts})



def post_share(request, post_id):
    post = get_object_or_404(Post, id = post_id, status = 'draft')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url)
            subject = f"{cd['name']} recomends you read '{post.title}'" 
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject,message, 'jafar.logist@gmail.com', [cd['to']])
            sent=True
    else:
        form = EmailPostForm()

    return render(request, 'blog/share.html', {'post': post, 'form':form, 'sent':sent})
