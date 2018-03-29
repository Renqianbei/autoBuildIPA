#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time

#发邮件所用
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

#fir token
fir_api_token = '34d6f526c9fdcf9afe90753cdb9bb837'

project_Name = 'Saas_M'
scheme = 'Saas_M'
#Release Debug
configuration = 'Release'
isDistribution = False


# 项目根目录
project_path = "/Users/renqianbei/work/saasMz"
#当前autoIpa.py 以及 plist 所在文件夹位置
#主执行文件的父级目录
autoPythonRoot = sys.path[0]
#autoPythonRoot = '/Users/renqianbei/work/saasMz/autoIPA'

#自动打包根目录
autoBuildDirRoot = '/Users/renqianbei/Desktop/saasM_Autobuild'
# 编译成功后.xcarchive所在目录
archive_dir = autoBuildDirRoot+'/archive'
# 编译后目录
build_path = autoBuildDirRoot+'/build'
# 打包后ipa存储目录
targerIPA_dir = autoBuildDirRoot+'/ipaDir'


#CA certificate
#发布证书
DistributionCodeSignIndentify = "iPhone Distribution: Beijingxxxxx "
DistributionProfile = ""
DistributionExportFileName = "Distribution_ExportOptions.plist"

#测试证书
DeveloperCodeSignIndentify = "iPhone Developer: Jxxxxxx)"
DeveloperProfile = ""
DeveloperExportFileName = "Develop_ExportOptions.plist"


#时间字符串
time_Tag = '%s'%(time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time())))

#xcodebuild export ipa包命令时需要用到
def export_OptionsPlist():
    if isDistribution :
        return autoPythonRoot+'/'+DistributionExportFileName
    else:
        return autoPythonRoot+'/'+DeveloperExportFileName

#使用证书
def CodeSignIdentify():
    if isDistribution:
        return DistributionCodeSignIndentify
    else:
        return DeveloperCodeSignIndentify

def ProvisioningProfile():
    if isDistribution:
        return DistributionProfile
    else:
        return DeveloperProfile


#打包名字
def archiveName():
    return project_Name+time_Tag+'.xcarchive'
#archive地址
def archivePath():
    return '%s/%s'%(archive_dir,archiveName())
#ipa包名
def ipafilename():
    return '%s_%s'%(project_Name,time_Tag)
#ipa导出地址
def exportpath():
    return '%s/%s'%(targerIPA_dir,ipafilename())




# 清理项目 创建build目录
def clean_project_mkdir_build():
    os.system('rm -rf %s;mkdir %s'%(build_path,build_path))

#archive  打包
def archive_project():
    print("====archive_project start")
    print(archiveName())
    os.system('cd %s; xcodebuild archive  -workspace  %s.xcworkspace  -scheme %s -configuration %s -archivePath %s CONFIGURATION_BUILD_DIR=%s CODE_SIGN_IDENTITY="%s" PROVISIONING_PROFILE="%s"'
              %(project_path,project_Name,scheme,configuration,archivePath(),build_path,CodeSignIdentify(),ProvisioningProfile())
              )


# 打包ipa 并且保存在桌面
def export_ipa():
  
    print("export_ipa start")
    print(ipafilename())
    print(export_OptionsPlist())
    os.system('xcodebuild -exportArchive -archivePath %s/ -exportOptionsPlist %s -exportPath %s'%(archivePath(),export_OptionsPlist(),exportpath()))



##上传到fir
def upload_fir():
    p = exportpath()+'/'+scheme+'.ipa'
    if os.path.exists(p):
        print('watting===%s...上传到fir'%p)
        # 直接使用fir 有问题 这里使用了绝对地址 在终端通过 which fir 获得
        ret = os.system('fir publish %s -T %s'%(p,fir_api_token))
        print('watting...上传结束')
        return True
    else:
        print("没有找到ipa文件")
        return False

#发邮件相关信息
from_addr = "liuhaohao@haokeduo.com"
password = "W123abc"
smtp_host = "smtp.exmail.qq.com"
to_addr = 'wangdongshan@haokeduo.com'
#'shizhongyan@haokeduo.com'

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

# 发邮件
def send_mail():
    msg = MIMEText(scheme+' iOS测试项目已经打包完毕，请前往 https://fir.im/jk7z 下载测试！', 'plain', 'utf-8')
    msg['From'] = _format_addr('自动打包系统 <%s>' % from_addr)
    msg['To'] = _format_addr('测试人员 <%s>' % to_addr)
    msg['Subject'] = Header(scheme+'iOS客户端app测试包', 'utf-8').encode()
    try:
        server = smtplib.SMTP(smtp_host, 25)# 25 为 SMTP 端口号
        server.set_debuglevel(1)
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()
        print('邮件发送成功')
    except smtplib.SMTPException:
        print('Error:无法发送邮件')



def main():
    # 执行

    # 清理并创建build目录
    clean_project_mkdir_build()
    # 编译coocaPods项目文件并 执行编译目录
    archive_project()
    # 导出ipa
    export_ipa()

    if not isDistribution:
    # 上传fir
        success = upload_fir()
    # 发邮件
        if success:
            send_mail()


main()
