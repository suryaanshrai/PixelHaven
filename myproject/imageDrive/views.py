from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from imageDrive.models import User, Image
from django.db import IntegrityError
from django.core.paginator import Paginator

    
def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "imageDrive/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "imageDrive/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "imageDrive/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "imageDrive/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "imageDrive/register.html")
    

def valid_image(image):
    """Checks if the given file is a valid image or not"""
    if not image.content_type.startswith("image/"):
        return "Uploaded file is not an image!"
    elif image.size > 15000000:
        return "Image larger than 5MB!"
    return True


def index(request):
    if request.user.is_authenticated:
        images = Image.objects.filter(user=request.user)
        paginator = Paginator(images, 10)
        page_obj = paginator.get_page(1)
        if request.method == "POST":
            image = request.FILES["image"]
            valid = valid_image(image)
            if valid is not True:
                return render(request, "imageDrive/home.html", {
                    "message":valid,
                    "images": page_obj,
                })
            new_image = Image(user=request.user, image=image)
            new_image.save()
            return HttpResponseRedirect(reverse("index"))
        elif request.method == "GET":
            try:
                page_no = request.GET["page_no"]
                page_obj = paginator.get_page(page_no)
            except:
                pass
            return render(request, "imageDrive/home.html", {
                "images":page_obj,
            })
    else:
        return render(request, "imageDrive/index.html")
    
def delete(request):
    id = request.POST["imgid"]
    image = Image.objects.get(id=int(id))
    if request.user != image.user:
        return HttpResponse("Invalid Request")
    image.delete()
    return HttpResponseRedirect(reverse("index"))