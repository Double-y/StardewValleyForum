from email import message
from multiprocessing import context
from django.shortcuts import render,HttpResponse,redirect
from .models import Room,Topic,Message,User
from .forms import RoomForm,UserForm,MyUserCreationForm,MyPasswordChangeForm,PasswordResetForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
import datetime
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone

def Welcome(request):
    return render(request,'app/welcome.html')
    
def LoginPage(request):
    page='login'

    if request.user.is_authenticated:
        return redirect('home')
    
    try:
        username=request.session['username']
        context={'page':page,'name':username}
    except:
        context={'page':page}
    
    if request.method=='POST':
        username=request.POST.get('name')
        password=request.POST.get('password')
        request.session['username']=username
        context={'page':page,'name':username}
        print('Username',username)
        print('Password',password)
        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request, '用户不存在')
            return render(request,'app/login_registration.html',context)
        
        user=authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, '用户名或密码错误')

    return render(request,'app/login_registration.html',context)

def LogoutPage(request):
    logout(request)

    return redirect('home')

def registerPage(request):
    page='register'
    form=MyUserCreationForm()
    if request.method=='POST':
        form=MyUserCreationForm(request.POST)
        # print(form)
        if form.is_valid():
            print('Inside VAlid')
            user=form.save(commit=False)
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'注册失败')
            print(form)
    context={'form':form,'page':page}
    return render(request,'app/login_registration.html',context)

def Home(request):
    q=request.GET.get('q','')
    room=Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    
    topics=Topic.objects.all()
    room_count=room.count()
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q))
    print('------------------------DATA---------------------------------',room)
    return render(request,'app/Home.html',{'room':room,'topics':topics,'room_count':room_count,'room_messages':room_messages})

def Rooms(request,pk):
    if request.user.is_authenticated:
        data=Room.objects.get(id=pk)
        room_messages=Message.objects.filter(room=data)
        participants=data.participants.all()
        print(room_messages)
        print('data',data)

        if request.method=='POST':
            message=Message.objects.create(
                user=request.user,
                room=data,
                body=request.POST.get('body')
            )
            data.participants.add(request.user)
            return redirect('room',pk=data.id)

        context={'room':data,'room_messages':room_messages,'participants':participants}
        return render(request,'app/Room.html',context)
    else:
        return redirect('login')

def userProfile(request):
    return render(request,'app/profile.html')
#1
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context={'form':form,'topics':topics,'topic_label':'主题','name_label':'房间名称','description_label':'房间描述'}
    return render(request,'app/room_form.html',context)

@login_required(login_url='login')
def updateMessage(request,pk):
    message=Message.objects.get(id=pk)
    room_id=message.room_id
    formmessage=message.body
    if request.method=='POST':
        message.body=request.POST.get('message')
        message.save()
        return redirect('room',pk=room_id)
    return render(request,'app/update-message.html',{'formmessage':formmessage})
#2
@login_required(login_url='login')
def updateRoom(request,pk):
    room=Room.objects.get(id=pk)
    form=RoomForm(instance=room)
    topics=Topic.objects.all()
    if request.user!= room.host:
        return HttpResponse('You are not allowed Here!!')
    if request.method=='POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context={'form':form,'topics':topics,'room':room}
    return render(request,'app/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)
    if request.user!= room.host:
        return HttpResponse('You are not allowed Here!!')
    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request,'app/delete.html',{'room':room})


@login_required(login_url='login')
def deleteMessage(request,pk):
    message=Message.objects.get(id=pk)
    if request.user!= message.user:
        return HttpResponse('You are not allowed Here!!')
    if request.method=='POST':
        room_id=message.room_id
        message.delete()
        return redirect('room',pk=room_id)
    return render(request,'app/delete.html',{'room':message})


def userProfile(request,pk):
    user=User.objects.get(id=pk)
    room=user.room_set.all()
    messages=user.message_set.all()
    topics=Topic.objects.all()
    context={'user':user,'room':room,'room_messages':messages,'topics':topics}
    return render(request,'app/profile.html',context)

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)

    return render(request, 'app/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'app/topicsPage.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'app/activity.html', {'room_messages': room_messages})

def sendOTP(email):
    # 生成验证码
    import random
    str1 = '0123456789'
    rand_str = ''
    for i in range(0, 6):
        rand_str += str1[random.randrange(0, len(str1))]
    # 发送邮件：
    # send_mail的参数分别是  邮件标题，邮件内容，发件箱(settings.py中设置过的那个)，收件箱列表(可以发送给多个人),失败静默(若发送失败，报错提示我们)
    message = "您的验证码是" + rand_str + "，5分钟内有效，请尽快填写"
    emailBox = []
    emailBox.append(email)
    send_mail('星露谷物语论坛', message, None, emailBox, fail_silently=False)
    return rand_str

def forgetPassword(request, activityId):
    successMessage = ''
    errorMessage = ''
    if activityId == 0:
        try:
            username = request.session.get('username')
        except:
            pass
        return render(request,'app/forget-password.html', {'username': username})
    elif activityId == 1:
        username = request.POST.get('username')
        email = request.POST.get('email')
        request.session['username'] = username
        request.session['email'] = email
        if User.objects.filter(username=username, email=email).exists():
            try:
                otp = sendOTP(email)
                request.session['email'] = email
                request.session['otp'] = otp
                request.session['otp_outdated'] = (timezone.now() + datetime.timedelta(minutes=5)).isoformat()
                request.session['attempt'] = 0
                successMessage = '验证码已发送至邮箱，请查收！'
            except:
                errorMessage = '验证码发送失败，请检查邮箱地址！'
        else:
            errorMessage = '邮箱地址不存在！'
        return render(request,'app/forget-password.html', {'username': username,'email': email,'successMessage': successMessage, 'errorMessage': errorMessage})
    elif activityId == 2:
        username = request.session.get('username')
        email = request.session.get('email')
        try:
            request.session['attempt'] += 1
            otp = request.POST.get('code')
            if otp == request.session.get('otp') and timezone.now() < datetime.datetime.fromisoformat(request.session.get('otp_outdated')) and request.session.get('attempt') < 4:
                del request.session['otp']
                del request.session['otp_outdated']
                del request.session['attempt']
                return redirect('change-password')
            elif request.session.get('attempt') <= 4 and otp != request.session.get('otp'):
                errorMessage = '验证码错误！还有' + str(4 - request.session.get('attempt')) + '次机会！'
            elif request.session.get('attempt') >= 5 or timezone.now() >= datetime.datetime.fromisoformat(request.session.get('otp_outdated')):
                del request.session['otp']
                del request.session['otp_outdated']
                del request.session['attempt']
                errorMessage = '验证码已失效，请重新获取！'
        except:
            errorMessage = '请获取验证码！'

        return render(request,'app/forget-password.html', {'username': username,'email': email,'successMessage': successMessage, 'errorMessage': errorMessage})


def changePassword(request):
    if request.user.is_authenticated:
        page = 'change'
        if request.method == 'POST':
            form = MyPasswordChangeForm(user=request.user, data=request.POST)
            if form.is_valid():
                user = form.save()
                # 重新认证用户
                user = authenticate(username=user.username, password=form.cleaned_data['new_password1'])
                if user is not None:
                    # 更新会话
                    login(request, user)
                    success = '密码更改成功'
                    return render(request, 'app/password_change.html', {'success': success, 'page': page})
                else:
                    # 如果认证失败，返回错误信息
                    messages.error(request, '密码更改成功，但登录失败。请使用新密码重新登录。')
                    return redirect('login')
        else:
            form = MyPasswordChangeForm(user=request.user)

        return render(request, 'app/password_change.html', {'form': form, 'page': page})

    else:
        page = 'forgot'
        if request.method == 'POST':
            username = request.session.get('username')
            form = PasswordResetForm(request.POST)
            if not username:
                # 如果 session 中没有 username，重定向到登录页面或显示错误
                return redirect('login')

            # 查找用户
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # 如果没有找到用户，重定向到登录页面或显示错误
                return redirect('login')

            # 处理密码重置表单
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                # 更新用户密码
                user.set_password(form.cleaned_data['new_password1'])
                user.save()

                # 更新 session 以使用新密码
                update_session_auth_hash(request, user)
                success = '密码更改成功'
                return render(request, 'app/password_change.html', {'success': success, 'page': page})
        else:
            form = PasswordResetForm()

        return render(request, 'app/password_change.html', {'form': form, 'page': page})
