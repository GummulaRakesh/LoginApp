import re
from django.utils import timezone
from django.shortcuts import render,redirect
from LoginApp.models import newuser
from django.http import HttpResponse
from django.core.mail import send_mail
import uuid
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password



# Create your views here.
def homepage(request):
    if 'username' in request.session:
        return render(request, "home.html")
    else:
        return redirect('login')

def SignupPage(request):
    if request.method == "POST":
        uname = request.POST['username']
        email = request.POST['Email1']
        mobile = request.POST['Mobilenumber']
        pass1 = request.POST['Password1']
        pass2 = request.POST['Password2']

        # Check if the username or email is already registered
        if newuser.objects.filter(Username=uname).exists() or newuser.objects.filter(Email1=email).exists():
            return HttpResponse("Username or email id is already registered")

        # Enforce that the username must contain only alphabets
        if not uname.isalpha():
            return HttpResponse("Username must contain only alphabets.")

        # Enforce that the MobileNumber must be a valid 10-digit integer
        try:
            mobile_int = int(mobile)
            if len(str(mobile_int)) != 10:
                raise ValueError("Invalid MobileNumber. It should be a 10-digit integer.")
        except ValueError:
            return HttpResponse("Invalid MobileNumber. It should be a 10-digit integer.")

        # Enforce that the email must be valid
        email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        if not bool(re.match(email_pattern, email)):
            return HttpResponse("Invalid email address.")

        # Check if passwords match
        if pass1 != pass2:
            return HttpResponse("Your password and confirm password are mismatch.")

        # Enforce password complexity (alphanumeric and special characters)
        if not re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z])(?=.*[@#$%^&+=!])(?=\S+$).{8,}', pass1):
            return HttpResponse("Password must contain at least 8 characters, including at least one digit, one letter, and one special character.")

        # Hash the password before saving
        hashed_password = make_password(pass1)

        # Create a new user instance and save it to the database
        my_user = newuser(Username=uname, Email1=email, MobileNumber=mobile, Password1=hashed_password, Password2=hashed_password)
        my_user.save()

        # Send an email to the user
        user_id = my_user.id
        subject = 'Welcome to YourWebsite!'
        message = f'Thank you for signing up, {uname}!\n\nYour account details:\nUser Id: {user_id}\nUsername: {uname}\nPassword: {pass1}\nEmail: {email}\nMobile: {mobile}'
        from_email = 'raks.marolix@gmail.com'  # Replace with your email
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

        return redirect('login')

    return render(request, "Signup.html")

def LoginPage(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        # Retrieve the user from the database based on the provided username
        try:
            user = newuser.objects.get(Username=username)
        except newuser.DoesNotExist:
            return HttpResponse("Username or password is incorrect!")

        # Compare the provided password with the stored hashed password
        if check_password(password, user.Password1):
            # If the passwords match, log the user in
            request.session['username'] = username
            return redirect('home')
        else:
            return HttpResponse("Username or password is incorrect!")

    return render(request, "Login.html")

def Logout(request):
    if 'username' in request.session:
        del request.session['username']
    return redirect('login')

def is_token_valid(user_obj):
    # Example expiration check (adjust as needed)
    expiration_time = timezone.now() - timezone.timedelta(hours=1)  # Assuming a 1-hour expiration

    return user_obj.Forgot_password_token is not None and user_obj.Token_created_at >= expiration_time

def send_forgot_password_mail(Email1, token):
    subject = 'Your forget Password link'
    email_message = f'Hi. Click on the link to reset your password: http://127.0.0.1:8000/changepassword/{token}/'
    email_from = settings.DEFAULT_FROM_EMAIL
    recepient_list = [Email1]
    send_mail(subject, email_message, email_from, recepient_list)
    return True

def ForgetPassword(request):
    if request.method == 'POST':
        email = request.POST.get('Email1')
        user_obj = newuser.objects.filter(Email1=email).first()
        
        if not user_obj:
            messages.error(request, 'No user found with this email address')
            return redirect('forgotpassword')

        # Generate a new UUID for the token
        token = str(uuid.uuid4())
        user_obj.Forgot_password_token = token
        user_obj.Token_created_at = timezone.now()
        user_obj.save()

        send_forgot_password_mail(email, token)
        messages.success(request, 'An email is sent')

        # return redirect('login')  # 'login' is the URL name for the login page

    
    return render(request, 'forgotpassword.html')
    return redirect('login')

def change_password(request, token):
    try:
        user_obj = newuser.objects.get(Forgot_password_token=token)
    except newuser.DoesNotExist:
        print("User not found with the given token:", token)
        return render(request, 'invalid_token.html')  

    if not is_token_valid(user_obj):
        print("Token is not valid for the user:", user_obj)
        return render(request, 'invalid_token.html')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            return render(request, 'changepassword.html', {'error_message': 'Passwords do not match'})

    # Hash the new password before saving
        hashed_password = make_password(new_password)

    # Update the user's password
        user_obj.Password1 = hashed_password
        user_obj.Password2 = hashed_password

        # Optionally, clear the forgot_password_token after the password is changed
        user_obj.Forgot_password_token = None

        # Save the user object with the updated password
        user_obj.save()

        return redirect('login')

    return render(request, 'changepassword.html')

def delete_account(request):
    if request.method == 'POST':
        # Check if the user is authenticated
        if 'username' in request.session:
            username = request.session['username']

            try:
                # Get the logged-in user and delete their account
                user = newuser.objects.get(Username=username)
                user.delete()

                # Log out the user
                del request.session['username']

                return redirect('login')
            except newuser.DoesNotExist:
                return HttpResponse("User not found.")
        else:
            return HttpResponse("User not authenticated.")
    else:
        return render(request, 'delete_account.html')


