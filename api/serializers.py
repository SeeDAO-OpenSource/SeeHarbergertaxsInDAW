from rest_framework import serializers
from .models import User
from .models import Advertise
from .models import Image

from django.contrib.auth import get_user_model



usermodel = get_user_model()

# 用户
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'useraddr', 'sns', 'advtimestart', 'advtimeend', 'price', 'upstreamuseraddr', 'txhash']


# 广告提交
class AdvertiseSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Advertise
        fields = ['id', 'useraddr', 'pcimage', 'mobimage']

# 审核
class AuditSerializer(serializers.HyperlinkedModelSerializer): 
    class Meta:
        model = Advertise
        fields = ['id','useraddr', 'pcimage', 'mobimage', 'audstatus', 'auddate']


# 广告查询
class AdvertiseListSerializer(serializers.HyperlinkedModelSerializer): 
    class Meta:
        model = Advertise
        fields = ['id', 'pcimage', 'mobimage', 'createdate', 'audstatus', 'auddate', 'useraddr']

class ImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image', 'type']