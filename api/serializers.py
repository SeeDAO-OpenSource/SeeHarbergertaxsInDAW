from rest_framework import serializers
from .models import Holder
from .models import Advertise
from .models import Image
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

usermodel = get_user_model()

# 用户
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        
# 持有者
class HolderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Holder
        fields = ['id', 'useraddr', 'sns', 'advtimestart', 'advtimeend', 'price', 'upstreamuseraddr', 'txhash']

# 广告提交
class AdvertiseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Advertise
        fields = ['id', 'useraddr', 'pcimage', 'mobimage', 'applymsg']

# 审核
class AuditSerializer(serializers.HyperlinkedModelSerializer): 
    class Meta:
        model = Advertise
        fields = ['id','useraddr', 'pcimage', 'mobimage', "createdate", 'audstatus', 'auddate', 'audmsg', 'applymsg']

# 广告查询
class AdvertiseListSerializer(serializers.HyperlinkedModelSerializer): 
    class Meta:
        model = Advertise
        fields = ['id', 'pcimage', 'mobimage', 'createdate', 'audstatus', 'auddate', 'useraddr']

# 图片
class ImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image', 'type']

