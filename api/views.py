from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from .verify import validate
import datetime
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth import logout

import uuid
from .models import Holder, Advertise
from .serializers import HolderSerializer, AdvertiseSerializer, AuditSerializer, AdvertiseListSerializer, ImageSerializer, UserSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10   # default page size
    page_size_query_param = 'size'  # ?page=xx&size=??
    max_page_size = 50 # max page size

# 用户相关视图集
class LoginViewSet(viewsets.ViewSet):
    def create(self, request):
        useraddr = request.data['useraddr']
        signature = request.data['signature']
        message = request.data['message']
        print(message)
        isValild = validate(msg=message,signature=signature, useraddr=useraddr)
        if isValild == False:
            return Response('Signature Error', status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=useraddr)
        except User.DoesNotExist:
            # 如果用户不存在，创建新用户
            user = User.objects.create_user(username=useraddr, password='')
        login(request, user)

        serializer = UserSerializer(user)
        return Response(serializer.data)

class LogoutViewSet(viewsets.ViewSet):
    def create(self, request):
        useraddr = str(request.user)
        signature = request.data['signature']
        message = request.data['message']
        print(message)
        isValild = validate(msg=message,signature=signature, useraddr=useraddr)
        if isValild == False:
            return Response('Signature Error', status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=useraddr)
        except User.DoesNotExist:
            # 如果用户不存在，可以在此处创建新用户
            user = User.objects.create_user(username=useraddr, password='')
        logout(request, user)

        serializer = UserSerializer(user)
        return Response(serializer.data)

# 持有者相关视图集
class HolderViewSet(viewsets.ViewSet):
    pagination_class = StandardResultsSetPagination
    def list(self, request):
        queryset = Holder.objects.all()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = HolderSerializer(page, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = Holder.objects.all()
        Holder = get_object_or_404(queryset, pk=pk)
        serializer = HolderSerializer(Holder)
        return Response(serializer.data)
    
    # 待删除
    def create(self, request):
        serializer = HolderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 广告相关视图集
class AdvertiseViewSet(viewsets.ViewSet):
    pagination_class = StandardResultsSetPagination

    # 获取审核通过数据
    def list(self, request):
        queryset = Advertise.objects.filter(audstatus=0)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = AdvertiseListSerializer(page, many=True, context={'request': request})
        return Response(serializer.data)
    
    # 筛选数据
    def retrieve(self, request, pk=None):
        queryset = Advertise.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = AdvertiseListSerializer(user, context={'request': request})
        return Response(serializer.data)

    # 广告数据新建
    def create(self, request):
        # 提交数据
        useraddr = str(request.user)
        pcimage = request.data['pcimage']
        mobimage = request.data['mobimage']
        applymsg = request.data['applymsg']
        signatureMsg = """useraddr:%s\npcimage:%s\nmobimage:%s\napplymsg:%s"""%(useraddr, pcimage, mobimage, applymsg)
        print(signatureMsg)
        isValild = validate(msg=signatureMsg,signature=request.data['usersignature'], useraddr=useraddr)
        if isValild:
            data = {'useraddr': useraddr, 'mobimage': mobimage, 'pcimage': pcimage, 'applymsg': applymsg}
            serializer = AdvertiseSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # 钱包验证不通过则返回 400
        return Response('Signature Error', status=status.HTTP_400_BAD_REQUEST)

    # 广告审核
    def partial_update(self, request, pk=None):
        queryset = Advertise.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        # 获取编号
        id = user.id
        useraddr = str(request.user)
        pcimage = user.pcimage
        mobimage = user.mobimage
        audstatus = request.data['audstatus']
        # 添加 审核时间
        auddate = datetime.datetime.now()
        audmsg = request.data['audmsg']
        data = {'id': id, 'useraddr': useraddr, 'mobimage': mobimage, 'audstatus': audstatus, 'auddate': auddate, 'audmsg': audmsg}
        serializer = AuditSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            signatureMsg = """id:%s\nuseraddr:%s\npcimage:%s\nmobimage:%s\naudstatus:%s\naudmsg:%s"""%(id, useraddr, pcimage, mobimage, audstatus, audmsg)
            print(signatureMsg)
            useraddr = "0xfF7ca7Fe8FdAF2a602191048E10A4b3B072aA1a0" # 审核地址
            isValild = validate(msg=signatureMsg,signature=request.data['audsignature'], useraddr=useraddr)
            if isValild:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED) 
            # 钱包验证不通过则返回 400
            return Response('Signature Error', status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 审核相关视图集，审核通过在 AdvertiseViewSet.partial_update
class AuditViewSet(viewsets.ViewSet):
    pagination_class = StandardResultsSetPagination
    def list(self, request):
        # 审核地址则返回所有数据
        if str(request.user) == "0xfF7ca7Fe8FdAF2a602191048E10A4b3B072aA1a0":
            queryset = Advertise.objects.all()
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            serializer = AdvertiseListSerializer(page, many=True)
            return Response(serializer.data)
        # 用户地址则返回用户数据
        queryset = Advertise.objects.filter(useraddr=request.user)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = AuditSerializer(page, many=True, context={'request': request}, )
        print(request.user)
        return Response(serializer.data)

# 图片上传
class ImageViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            imageFile = request.FILES.get('image')
            imageExtension = imageFile.name.split('.')[-1]  # 获取图片扩展名
            imageName =  f"{uuid.uuid4().hex}.{imageExtension}"  # 使用随机名称
            request.FILES['image'].name = imageName # 修改图片名称
            serializer.save(image=imageFile)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)