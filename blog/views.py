from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from .models import Post
from .forms import EmailPostForm

# Create your views here.
def post_list(request):
    object__list = Post.objects.all()
    paginator = Paginator(object__list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request,'blog/list.html', {'posts': posts})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug = post, status = 'draft', publish__year = year, publish__month = month, publish__day = day)
    
    return render(request, 'blog/detail.html', {'post': post})

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
