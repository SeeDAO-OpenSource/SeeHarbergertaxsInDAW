from django.db import models
from django.contrib.auth import get_user_model
import datetime


# 用户表
class Holder(models.Model):
    id = models.AutoField(verbose_name='用户ID', db_index=True, primary_key=True)
    useraddr = models.CharField(verbose_name='用户钱包地址', max_length=1024, )
    sns = models.CharField(verbose_name='SNS名称', max_length=1024, blank=True, null=True)
    advtimestart = models.DateTimeField(verbose_name='拥有广告牌开始时间，即购买时间')
    advtimeend = models.DateTimeField(verbose_name='拥有广告牌结束时间')
    price = models.DecimalField(verbose_name='购买价格', decimal_places=8, max_digits=100000)
    upstreamuseraddr = models.CharField(verbose_name='上游用户钱包地址', max_length=1024)
    txhash = models.CharField(verbose_name='交易哈希值', max_length=1024, blank=True, null=True)

    def __str__(self):
        return self.useraddr

    class Meta:
        ordering = ['-advtimestart']
        verbose_name = "Holder"
# 广告表
class Advertise(models.Model):
    audStatusChoices = (
        (0, '审核成功'),
        (1, '审核失败'),
        (2, '审核中')
    )

    id = models.AutoField(verbose_name='广告ID', db_index=True, primary_key=True)
    useraddr = models.CharField(verbose_name=("所属用户钱包地址"), max_length=1024)
    pcimage = models.CharField(verbose_name='pc图片路径', max_length=1024)
    mobimage = models.CharField(verbose_name='移动端图片路径', max_length=1024)
    audstatus = models.CharField(verbose_name='审核状态, 审核成功|审核失败|审核中', default=2, max_length=1024, choices=audStatusChoices)
    createdate = models.DateTimeField(verbose_name='广告提交时间', default=datetime.datetime.now())
    auddate = models.DateTimeField(verbose_name='广告审核时间', blank=True, null=True)
    usersignature = models.CharField(verbose_name='用户签名', max_length=1024, blank=True, null=True)
    usersignaturemsg= models.CharField(verbose_name='用户签名内容', max_length=1024, blank=True, null=True)
    applymsg = models.CharField(verbose_name="申请留言", max_length=1024, blank=True, null=True)
    audsignature = models.CharField(verbose_name='审核签名', max_length=1024, blank=True, null=True)
    audsignaturemsg = models.CharField(verbose_name='审核签名内容', max_length=1024, blank=True, null=True)
    audmsg = models.CharField(verbose_name="审核留言", max_length=1024, blank=True, null=True)

    def __str__(self):
        return self.id

    class Meta:
        ordering = ['-id']
        verbose_name = "Advertise"

# 图片表
class Image(models.Model):
    imageTypeChoices = (
        (0, 'PC端图片'),
        (1, '移动端图片'),
    )
    id = models.AutoField(verbose_name='图片ID', db_index=True, primary_key=True)
    image = models.ImageField(upload_to='img/')
    type = models.CharField(verbose_name='图片类型，PC图片|移动端图片', max_length=1024, choices=imageTypeChoices)
    createdate = models.DateTimeField(verbose_name='广告提交时间', default=datetime.datetime.now())


    class Meta:
        verbose_name = "Image"