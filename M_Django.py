# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 21:32:21 2023

@author: Administrator
"""

import pathlib
import chardet
import subprocess
import os, sys
import django


class Para_App:
    '''
    包装应用相关的参数
    '''
    def __init__(self, app_name, fun_num ):
        
        self.app_name = app_name        # 应用名（未加 'App' 后缀）
        self.fun_num  = fun_num         # 应用下的视图函数数目（功能数）
        
        
class Para_Prj:
    
    def __init__(self, parent_dir, prj_name, apps ):
        
        self.parent_dir = parent_dir        # 项目主目录父目录
        
        self.prj_name = prj_name
        
        self.apps = apps                # [Para_App]型，应用参数列表
        
        self.static = "static"
        
        self.media = "media"
        
        self.templates = "templates"
        
        
 
def _get_prj_path( para_prj ):
    
    return  "{0}/{1}/".format( para_prj.parent_dir, para_prj.prj_name)
    

def _get_insert_pos( main_str, flag_section, flag_text, start=0 ):
    '''
    获取具有容器特征的某结构的结束位置（追加模式的插入位置）
    通常可用 flag_section 定位至某小节；再用 flag_text 定位至节内的具体位置。
    只返回标志位，具体插入由上级程序决定
    
    Parameters
    ----------
    main_str : string
        主串.
    flag_section : string
        本小节标题（开始位置）.
    flag_text : string
        本小节结束标志（默认在其前面插入）.
    start : int
        搜索的开始位置
    Returns : 本节的结束标志
    -------
    '''
    
    idx1 = main_str.find(flag_section, start)
    
    idx2 = main_str.find(flag_text, idx1 + len(flag_section) )
    
    return idx2
    

def _get_encoding( file ):
    '''
    获取文件的编码

    Parameters
    ----------
    file : 文件对象
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    with file.open('rb') as handle:
        
        code_str = handle.read( )
        
        dicts = chardet.detect( code_str )
        
        #print('in _get_encoding, 文件编码：', dicts["encoding"])
        
        return dicts["encoding"]
    
    
    
def _build_django_paths( para_prj, home_name = 'home'):
    '''
    生成 urls.py 中所需的源代码（暂不考虑二级路由）
    利用 Para_Prj 中所包装的参数生成对应的 path 语句
    由于暂不支持二级路由，这里采用 应用名 + 功能编号 的方式来生成所有的虚拟路径
        如：应用名为 'demo'
    后续的 视图函数名，甚至网页名也如法生成。
    
    Parameters
    ----------
    para_prj : Para_Prj
        项目的参数对象
    home_name : 首页（应用）名
    Returns
    -------
    None.

    '''
    paths = []

    for app in para_prj.apps:
        
        path_str ="    # {0}\n".format( app.app_name )  # 添加一个应用名作为注释
        paths.append( path_str )

        if app.app_name == home_name:
            path_str = "    path('',{0},name='{0}'),\n".format(home_name)

        for i in range( app.fun_num ):

            fun_name = "{0}_{1}".format(app.app_name, i+1)

            if app.app_name == home_name:
                path_str = "    path('',{0},name='{0}'),\n".format(fun_name)
            else:
                path_str = "    path('{0}/',{0},name='{0}'),\n".format( fun_name )
                    
            paths.append( path_str )
            
            
    all_paths_str = "".join( paths )
    
    #print( all_paths_str )
    
    return all_paths_str
    

def _build_path_imports( para_prj ):
    '''
    生成 urls.py 顶部的用于导入视图函数的导入语句
    
    Parameters
    ----------
    para_prj : Para_Prj
        项目的参数对象
    Returns
    -------
    None.

    '''
    
    imports = []

    for app in para_prj.apps:
        
        funs = []
        
        for i in range( app.fun_num ):
            
            if i == 0:
                
                funs.append( "{0}_{1}".format( app.app_name, i+1 ) )
                
            else:
                    
                funs.append( ",{0}_{1}".format( app.app_name, i+1 ) )
            
        funs_str = "".join( funs )
            
        imports.append( "from {0}.views import {1}\n".format( app.app_name, funs_str) )
        
    imports.append("\n")
        
    imports_str = "".join( imports ) 
    
    #print( imports_str )
      
    return imports_str 
      
def _get_apps_register_str( para_prj ):
    '''
    生成写入 settings.py 文件 INSTALLED_APPS 节中的注册子串
    Parameters
    ----------
    para_prj : Para_Prj
        项目的参数对象
    Returns
    -------
    None.

    '''
    apps = para_prj.apps
    
    app_list = []
    
    for app in apps:
        app_list.append( "    '{0}'".format(app.app_name ) )  
        app_list.append( ',\n')
    
    return "".join(app_list)

            
def create_apps( para_prj ):
    
    prj_name = para_prj.prj_name
    
    # 创建项目
    # res_prj = subprocess.run(['django-admin','startproject', prj_name ], stdout=subprocess.PIPE)
    res_prj = subprocess.run([ sys.executable, '-m', 'django', 'startproject', prj_name], stdout=subprocess.PIPE)

    print('创建项目{0}...完成；'.format( prj_name ) )
    
    # 进入子目录
    os.chdir( prj_name )
    
    # 创建各应用
    for app in para_prj.apps:
        res_app = subprocess.run([ sys.executable, 'manage.py', 'startapp', '{0}'.format(app.app_name)],
                                 stdout=subprocess.PIPE)
        
        #res_app = subprocess.run(['python', 'manage.py'.format(prj_name), 'startapp', '{0}'.format( app.app_name) ], 
        #                         stdout=subprocess.PIPE)
        
        print('...生成应用："{0}" '.format( app.app_name ) )

    if not os.path.exists('static'):
        os.mkdir('static')
    if not os.path.exists('media'):
        os.mkdir('media')
    if not os.path.exists('templates'):
        os.mkdir('templates')
    
    # 退出项目主目录
    os.chdir("..")
    # print( "当前目录：",os.path.abspath(".") )
    
    return res_prj
    
        
def write_path( para_prj ):
    '''
    修改路由文件，添加各路由项（但目前只支持一级路由）

    Parameters
    ----------
    para_prj : Para_Prj
        项目的参数对象

    Returns
    -------
    None.
    '''
    
    print("创建路由信息...")
    
    file_name = "{0}/{1}/{1}/urls.py".format( para_prj.parent_dir, para_prj.prj_name)
    
    
    file = pathlib.Path( file_name )
    
    # path_name 为虚拟路径名，同样，视图函数也用这个名
    
    encode = _get_encoding( file )
    
    new_str = ""
     
    with file.open('r', encoding = encode) as handle:
        
        code_str = handle.read()
        
        s_pos = _get_insert_pos( code_str, '"""', '"""')    # 跳过注释
        imp_pos = _get_insert_pos( code_str, "from", 'urlpatterns =', s_pos)    
        url_pos = _get_insert_pos( code_str, "urlpatterns", ']', imp_pos )
        
        imports_str = _build_path_imports( para_prj )
        
        #print("IMPORT_STR:", imports_str )
        
        paths_str = _build_django_paths( para_prj )
        
        new_str = code_str[:imp_pos] + imports_str + code_str[imp_pos:url_pos] + \
                     paths_str + code_str[url_pos:]
    
        #print( "文件内容：{!r}".format( handle.read() ) )
        
        #handle.seek(0)
        
    with file.open('w', encoding = encode) as handle:
        
        handle.write( new_str )
        
    print("...路由设置完成.")
    
    
def write_settings( para_prj ):
    '''
    修改 settings.py 文件
    Parameters
    ----------
    para_prj : Para_Prj
        项目的参数对象
        para_prj.apps[];        //待注册的应用名
        para_prj.static;        //静态子目录
        para_prj.templates;     //主目录下的模板目录 
    file_name : string
        文件名，可带路径.
    Returns
    -------
    None.
    '''
    print("创建注册信息...")
    par_dir = para_prj.parent_dir
    # print( '父目录', par_dir)
    
    prj_dir = para_prj.prj_name
    file_name= 'settings.py'

    # 项目名下的同名二级子目录存放 settings.py 
    file = pathlib.Path( '{0}/{0}/{1}'.format( prj_dir, file_name ) )
    
    #print("配置文件全路径", file )
    
    new_str =""   # 存放插入后的代码
    
    with file.open('r+') as handle:
        
        code_str = handle.read()
        
        # 找出几个关键插入点
        
        # 导入语句的位置
        pos_import = _get_insert_pos( code_str, '"""', '"""' ) + len('"""')
        
        pos_apps   = _get_insert_pos( code_str, 'INSTALLED_APPS', ']' )
        
        pos_dirs   = _get_insert_pos( code_str, 'DIRS', ']' )
        
        # 导入串的合成
        import_str = "\nimport os\n"
        
        # 注册应用
        # app_str = "\n    'test',"       # 测试用
        app_str = _get_apps_register_str( para_prj )
        
        # 注册主目录下的 templates 目录
        t_str = "os.path.join(BASE_DIR, 'templates')"
        
        # 注册 static 目录
        s_str1 = "STATICFILES_DIRS = ( \n"
        s_str2 = "    os.path.join(BASE_DIR, 'static'), \n"
        s_str3 = ") \n"
        
        static_str ="".join( (s_str1, s_str2, s_str3) )
        
        
        # 注册 media 目录
        m_str1 = "MEDIA_URL = '/media/'\n"
        m_str2 = "MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')\n"
        
        media_str = "".join( (m_str1, m_str2) )
        
        
        section_tuple =( code_str[: pos_import ], import_str,
                         code_str[pos_import : pos_apps],  app_str,
                         code_str[pos_apps : pos_dirs],    t_str,
                         code_str[pos_dirs : ],            static_str,
                         media_str
                       )
        
        new_str = "".join( section_tuple )
        
    with file.open('w') as handle:    # 这次是写模式打开
        
        handle.write( new_str )
    
    print( "...应用注册完成")
        
    return
        

def _build_view_fun_str( para_prj ):
    '''
    生成视图函数定义代码文本
    Parameters
    ----------
    para_prj : Para_Prj
        项目的参数对象
        DESCRIPTION.

    Returns
    -------
    dicts : TYPE
        DESCRIPTION.

    '''
    append_str =""
    
    app_num = len( para_prj.apps )
    
    dicts={}                       # 定义一个空字典，用于存放结果
    
    for i in range( app_num ):
        
        #print( "Begin" + str(i+1) )
        
        web_num = para_prj.apps[i].fun_num    # 每个视图函数对应一个网页
        
        append_str = ""
        
        append_list = []
        # para_prj.apps[i] 为第i个应用名；para_prj.webs[i] 为第i个应用下的网页数
        for j in range( web_num ):
            
            # 采用 “应用名+功能序号” 作为函数名，同时也是网页名（不包括扩展名）、虚拟路径名
            fun_name = para_prj.apps[i].app_name + "_" + str(j+1)
            
            append_list.extend( [
                "def {}(request):\n".format( fun_name ),
                "    #\n",
                "    return render( request,'{}.html')\n\n".format( fun_name )
                ]
            )
             
            #print( "@@", append_tuple )
            print( "...生成 '{0}'下的视图函数 '{1}()';".format( para_prj.apps[i].app_name, fun_name ))
            
        append_str = "".join( append_list )
        
        # 设置（追加）应用名与对应的 views.py 代码
        dicts[ para_prj.apps[i].app_name ] = append_str 
            
    # 返回各应用中的视图函数（用字典存放，键名为应用名）
    return dicts

def write_views( para_prj, file_name='views.py' ):
    '''
    写（所有的）视图文件
    Parameters
    ----------
    para_prj : Para_Prj
        项目的参数对象,其内参数：
        para_prj.apps[];        //待注册的应用名
        para_prj.static;        //静态子目录
        para_prj.templates;     //主目录下的模板目录 
        
    app_name : string       
        应用名
    file_name : string      
        视图函数文件名，可带路径.
    Returns
    -------
    None.
    '''
    
    #code_str = ""                               # 用于接收从文件中读到的串
    print("创建视图函数...")
    
    dicts = _build_view_fun_str( para_prj )
    
    par_dir = para_prj.parent_dir     # 取项目名
    prj_dir = para_prj.prj_name
    
    for k, v in dicts.items():
        
        a_dir = k       # 取应用名
        
        v_file = file_name
        
        # 合成视图函数的目录
        file = pathlib.Path( '{0}/{1}/{2}/{3}'.format( par_dir, prj_dir, a_dir, v_file ) )
        
        encode = _get_encoding( file )          # 获取编码
        
        with file.open('a', encoding = encode ) as handle:
            
            handle.write( v )
        
    return
    

def _read_from_file(filename):
    
    # 获取模板网页
    file = pathlib.Path( filename )
    
    encode = _get_encoding( file )          # 获取编码

    try:
        with file.open('r', encoding = encode ) as handle:
        
            content_str = handle.read()
    except OSError as e:
        # e 是异常对象，包含错误类型、错误号、错误描述等信息
        print(f"【错误类型】：{type(e).__name__}")
        print(f"【错误编号】：{e.errno}")  # 系统级错误编号（如文件不存在对应2）
        print(f"【错误描述】：{e.strerror}")  # 可读的错误信息
        print(f"【涉及文件】：{e.filename}")  # 触发异常的文件名
    
    return content_str, encode


def _write_to_file(full_name, content_str, encoding ='UTF-8' ):
    '''
    将字符串写入文件
    Parameters
    ----------
        full_name :
        项目的参数对象
        content_str:
        内容串
    Returns
    -------
    None.
    '''

    file = pathlib.Path(full_name)

    try:
        with file.open('w', encoding = encoding ) as handle:
            handle.write(content_str)
    except OSError as e:
        # e 是异常对象，包含错误类型、错误号、错误描述等信息
        print(f"【错误类型】：{type(e).__name__}")
        print(f"【错误编号】：{e.errno}")  # 系统级错误编号（如文件不存在对应2）
        print(f"【错误描述】：{e.strerror}")  # 可读的错误信息
        print(f"【涉及文件】：{e.filename}")  # 触发异常的文件名


def _get_templates_path( prj_path, app_name):

    if app_name == '':
        template_path = "{0}templates".format(prj_path)
    else:
        template_path = "{0}{1}/templates".format(prj_path, app_name )
    # 若目录未创建，则创建
    if not os.path.exists(template_path):
        os.mkdir(template_path)

    return  template_path

def write_html( para_prj ):
    '''
    生成所有 HTML文件
    Parameters
    ----------
    para_prj : Para_Prj
        项目的参数对象

    Returns
    -------
    None.

    '''
    print("创建网页模板...")

    # 获取模板数据
    prj_path = _get_prj_path( para_prj )    # 获取项目主目录

    base_src_str, encode = _read_from_file('base.html')
    #print('base_code:', encode)

    # 写基础网页: 先获取路径，
    base_html_path = _get_templates_path(prj_path, '')
    full_name = "{0}/base.html".format(base_html_path)
    # 再写
    _write_to_file(full_name, base_src_str, encode)

    # 写各应用网页，先获取模板串
    html_src_str, encode2 = _read_from_file('m.html')
    '''所有网页统一一种字符集，以 base.html 模板为准'''

    # 获取所有的 path
    paths_str = _build_django_paths( para_prj ).replace('\n','<br>')

    # 依次建立每个应用下的功能网页
    for para_app in para_prj.apps:
        # 获取当前应用子目录
        app_html_path = _get_templates_path(prj_path, para_app.app_name)

        # 依次建立同一个应用下的各个网页
        for i in range( 1, para_app.fun_num + 1 ):

            # 获取当前应用下的第 i 个 Web 模板的全路径
            web_full_name = "{0}/{1}_{2}.html".format(app_html_path, para_app.app_name, i)

            # 当前页面的名称
            web_name = "{0}_{1}".format(para_app.app_name, i )
            html_str = html_src_str.replace('###block_title###', web_name +'的标题，待进一步设置' )
            html_str = html_str.replace('###block_content###', web_name +'的内容，待进一步建设<br>' + paths_str )
            #html_str = html_template.format( "{0}_{1}".format(para_app.app_name, i ) )

            _write_to_file( web_full_name, html_str, encode)
            #encode = _get_encoding( file )          # 获取编码

            #with file.open('w') as handle:

            #    handle.write( html_str )
                
            print("...生成网页模板 '{0}'；".format( web_full_name ) )






 



 
