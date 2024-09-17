* https://dash.cloudflare.com/sign-up
* 云部署需要注意
***
git仓库部署后直接分配域名后面加文件名即可访问
***
如要自定义域名，域名格式必须为 自定义别名.x.x.x
***
自己域名站添加CNAME记录时 名称：自定义别名 数据：x.x.x. 最后必须加上. 否则CNAME配置失败
***
# 安装运行库清华源附加代码
 *  -i https://pypi.tuna.tsinghua.edu.cn/simple

***
 # py打包exe代码
* pyinstaller -F -c *.py   无图标
***
* pyinstaller -F -c -i *.ico *.py   带图标
* 
