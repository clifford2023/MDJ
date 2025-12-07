# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 10:39:46 2023

@author: Hong Yao.
"""

import M_Django as dj


'''
    本工具目标是快速创建一个 django 项目，避免参数的繁杂配置，
    主要用于初学者练习和教学之用（v0.3版修正了原来的bug，可运行版），
    为达到此目标，拟添加一些规则，但也约束了一定的自由度：
    （1）目前只生成一级路由;
    （2）虚拟路径、视图函数前缀、网页前缀同名，都用应用名；
    （3）一个网页中的多个网页、视图函数添加后缀 ’_<i>‘, 其中 '<i>'
        为当前应用下第 i 个同类对象，如有个应用名为：'about',则该
        应用下的第 1，2个视图函数分别为 'about_1()', 'about_2()'，
        而其对应的网页分别为：'about_1.html', 'about_2.html'
    （4）视图函数中默认只导向模板网页，即用 render 函数，若需要返回
            数据（如用 ajax 模式），则可在生成框架后再修改。

    使用方法：
    （1）编辑 MDJ.py 文件，修改相关参数：
            project_name = "P1"             # 项目名
            
            app_paras = [['app1', 3 ],      # 分别应用名，该应用下拟建的页面数
                     ['app2', 2 ],
                     ['app3', 4 ],
                    ]
    （2）运行： "python MDJ.py"，即可在当前目录下生成项目框架
    
'''

def initpara_prj():
    '''
    Returns
    -------
    para_prj : TYPE
        DESCRIPTION.

    '''
    
    project_name = "K9"               # 项目名

    app_paras = [['home', 1],          # 作为首页菜单，建议不改动路径
                 ['inputApp', 3 ],      # 分别应用名，该应用下拟建的页面数
                 ['buildApp', 3 ],
                 ['QueryApp', 2],
            ]
    
    # 目前还未构建错误检查，下列的应用名切忌同名，否则后续会出错
    
    apps =[]
    
    for para in app_paras:
        apps.append( dj.Para_App( para[0], para[1] ))
                    
    # Para_App中的两参数依次为：应用名，应用下的页面个数
    # apps.append( dj.Para_App('app1', 3 ) )
    # apps.append( dj.Para_App('app2', 2 ) )
    #apps.append( Para_App('name3', 4 ) )
    
    # 参数依次为：当前目录（项目的父目录），项目名， 应用参数集合（即上面建的列表）
    para_prj = dj.Para_Prj('.', project_name, apps)
    
    return para_prj

if __name__ == '__main__':
    
    para_prj = initpara_prj()
        
    dj.create_apps( para_prj )     # 创建项目及应用集

    dj.write_settings( para_prj )  # 进行相关的设置（如注册应用等）
     
    dj.write_path( para_prj )      # 创建路由（目前只支持一级路由）

    dj.write_views( para_prj )     # 创建视图函数

    dj.write_html( para_prj )      # 创建模板网页