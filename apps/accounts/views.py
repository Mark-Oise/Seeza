# from django.shortcuts import render, redirect
# from django.contrib.auth import login
# from django.http import HttpResponse
# from django.views.decorators.http import require_http_methods
# from .models import CustomUser
# from django.core.mail import send_mail
# import random


# def generate_verification_code():
#     return ''.join([str(random.randint(0, 9)) for _ in range(6)])


# @require_http_methods(["GET", "POST"])
# def login_view(request):
#     if request.method == "GET":
#         return render(request, "account/login.html")

#     email = request.POST.get("email")
#     user, created = CustomUser.objects.get_or_create(email=email)

#     verification_code = generate_verification_code()
#     user.set_verification_code(verification_code)

#     send_mail(
#         'Your verification code',
#         f'Your verification code is: {verification_code}',
#         'from@example.com',
#         [email],
#         fail_silently=False,
#     )

#     return render(request, "account/partials/verify_email_form.html", {"email": email})


# @require_http_methods(["POST"])
# def verify_code(request):
#     email = request.POST.get("email")
#     code = ''.join([request.POST.get(f"code-{i}") for i in range(1, 7)])

#     user = CustomUser.objects.get(email=email)

#     if user.is_verification_code_valid(code):
#         login(request, user)
#         return HttpResponse(status=200)
#     else:
#         return HttpResponse("Invalid or expired code", status=400)


# @require_http_methods(["GET"])
# def go_back(request):
#     return render(request, "account/partials/login_form.html")
