from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from .verify import validate
import datetime
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser, JSONParser
from rest_framework.pagination import PageNumberPagination

import uuid
from .models import User, Advertise, Image
from .serializers import UserSerializer, AdvertiseSerializer, AuditSerializer, AdvertiseListSerializer, ImageSerializer

class MyPageNumberPagination(PageNumberPagination):
    page_size = 2   # default page size
    page_size_query_param = 'size'  # ?page=xx&size=??
    max_page_size = 10 # max page size


# 用户相关视图集
class UserViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    # 待删除
    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 广告相关视图集
class AdvertiseViewSet(viewsets.ViewSet):
    pagination_class = MyPageNumberPagination

    # 获取数据
    def list(self, request):
        queryset = Advertise.objects.all()
        serializer = AdvertiseListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    # 筛选数据
    def retrieve(self, request, pk=None):
        queryset = Advertise.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = AdvertiseListSerializer(user, context={'request': request})
        return Response(serializer.data)

    # 广告数据新建
    def create(self, request):
        serializer = AdvertiseSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # 提交数据
            useraddr = request.data['useraddr']
            pcimage = request.data['pcimage']
            mobimage = request.data['mobimage']
            applymsg = request.data['applymsg']
            signatureMsg = """useraddr:%s\npcimage:%s\nmobimage:%s\napplymsg:%s"""%(useraddr, pcimage, mobimage, applymsg)
            print(signatureMsg)
            isValild = validate(msg=signatureMsg,signature=request.data['usersignature'], useraddr=useraddr)
            if isValild:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            # 钱包验证不通过则返回 400
            return Response('Signature Error', status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 广告审核
    def partial_update(self, request, pk=None):
        queryset = Advertise.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        # 获取编号
        id = user.id
        useraddr = request.data['useraddr']
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


# 图片上传
class imageViewSet(viewsets.ViewSet):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = Image.objects.all()
    
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
