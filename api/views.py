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
from .audit import AuditClass 
import uuid
import base64
import logging
from .models import Holder, Advertise
from .serializers import HolderSerializer, AdvertiseSerializer, AuditSerializer, AdvertiseListSerializer, ImageSerializer, UserSerializer

AuditClass = AuditClass()
LOG_FORMAT = "%(asctime)s - %(filename)s[%(lineno)d] - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10   # default page size
    page_size_query_param = 'size'  # ?page=xx&size=??
    max_page_size = 50 # max page size
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })

# 用户相关视图集
class LoginViewSet(viewsets.ViewSet):
    def list(self, request):
        useraddr = str(request.user)
        try:
            user = User.objects.get(username=useraddr)
        except:
            return Response("User is not logged in", status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserSerializer(user)
        response_data = serializer.data.copy()
        # 是否为审核员
        if AuditClass.verify_audit(useraddr=useraddr):
            response_data['auditor'] = True
        else:
            response_data['auditor'] = False
        logging.info(useraddr)
        return Response(response_data)

    def create(self, request):
        useraddr = request.data['useraddr']
        signature = request.data['signature']
        message_base64 = request.data['message']
        # message base64 decode
        try:
            message = base64.b64decode(message_base64).decode()
        except:
            return Response("Message Error", status=status.HTTP_400_BAD_REQUEST)
        logging.info(message)
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
        response_data = serializer.data.copy()
        # 是否为审核员
        if AuditClass.verify_audit(useraddr=useraddr):
            response_data['auditor'] = True
        else:
            response_data['auditor'] = False
        logging.info(useraddr)
        return Response(response_data)

class LogoutViewSet(viewsets.ViewSet):
    def create(self, request):
        useraddr = str(request.user)
        signature = request.data['signature']
        message = request.data['message']
        logging.info(message)
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
        return paginator.get_paginated_response(serializer.data)
    
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
        return paginator.get_paginated_response(serializer.data)
    
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
        # 持有者判断
        pass

        pcimage = request.data['pcimage']
        mobimage = request.data['mobimage']
        applymsg = request.data['applymsg']
        signatureMsg = """useraddr:%s\npcimage:%s\nmobimage:%s\napplymsg:%s"""%(useraddr, pcimage, mobimage, applymsg)
        logging.info(signatureMsg)
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
        useraddr = user.useraddr
        # 审核员判断
        if AuditClass.verify_audit(useraddr) is False:
            return Response("Non-auditor", status=status.HTTP_401_UNAUTHORIZED)

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
            logging.info(signatureMsg)
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
        useraddr = str(request.user)
        # 默认返回任意审核状态
        audstatus = int(request.query_params.get('audstatus', 1000))

        # 审核地址则返回所有用户数据
        if AuditClass.verify_audit(useraddr) is True:
            queryset = Advertise.objects.all()
            if audstatus != 1000:
                queryset = queryset.filter(audstatus=audstatus)

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            serializer = AuditSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        # 用户地址则返回用户数据
        queryset = Advertise.objects.filter(useraddr=useraddr)
        if audstatus != 1000:
            queryset = queryset.filter(audstatus=audstatus)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = AuditSerializer(page, many=True, context={'request': request}, )
        logging.info(useraddr)
        return paginator.get_paginated_response(serializer.data)

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