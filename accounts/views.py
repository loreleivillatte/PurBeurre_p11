from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate


from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from accounts.forms import RegistrationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required


def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = request.POST['username']
            password = request.POST['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('profile')
    else:
        form = RegistrationForm()

    args = {'form': form}
    return render(request, 'accounts/registration.html', args)


@login_required
def view_profile(request):
    """ personal page of the user """
    return render(request, 'accounts/profile.html')




def logout_view(request):
    """ log a user out -> redirect to a success page"""
    logout(request)
    return redirect('index')
