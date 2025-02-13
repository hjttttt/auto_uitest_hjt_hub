# 框架简介

## 一、运行流程图
![流程图](/assets/框架架构图.png)

### gif动图效果，如下：
![用例gif动图](/assets/Test_ywxq_bj_2024-10-23_105036.gif)

### Html报告效果，如下：
![用例gif动图](/assets/html截图.png)

## 二、框架级功能

| 功能名称          | 实现原理                                                                  | 作用                                              |
|---------------|-----------------------------------------------------------------------|-------------------------------------------------|
| 解析excel用例     | 利用openpyxl库，读取excel数据，并编写函数解析特定数据，构造出固定格式的数据结构，供test函数模板和Test类模板调用填充  | 读取excel中的用例，并解析构造为固定格式的数据结构（一般为json对象）          |
| test_func模板   | 预编写test函数模板, 给自动生成的test方法，提供模板代码块                                     | 提供统一的test方法代码体，也便于维护                            |
| Test类模板       | 利用jinja2库，构造一个.j2模板文件来动态创建Test类的代码体                                   | 将excel中的每个流程用例，自动转换为python的Test类                |
| BaseDriver基类  | 在基类中定义好Webdriver实例的初始化、前置操作、后置操作                                      | 供Test类继承使用，eg: 执行每条用例前，需要登录并窗口最大化；执行完毕后，需要关闭浏览器 |
| components组件库 | 按组件维度，封装每个组件的属性、功能操作                                                  | 供关键字直接调用组件，也便于维护和拓展                             |
| KeyWordLib类   | 编写一些通用的Webdriver操作，eg(二次包装): click、input、find_element、sleep_until_ele等 | 该类中，封装一些通用的浏览器操作做为关键字，供test步骤调用                 |
| logger模块      | 比较简单，略过                                                               | 记录test方法的执行日志                                   |
| auth模块        | 授权相关，eg:自动登录、登录加密、用户cookie获取、token获取                                  | 调用登录接口，登录后获取到用户的身份认证信息，实现”切换用户“关键字              |
| screenshot模块  | 提供保存PNG截图、PNG截图转gif动图等功能                                              | 在每个test步骤的关键字执行时，截取PNG图片，并把用例中的所有步骤图片生成一个gif动图  |
| report模块      | 收集测试过程、结果数据，渲染生成HTML报告/text报告                                         | 更直观感知测试结果gif、报错截图                               |
| variable模块    | 采用变量占位填充方式，对excel中的关键字参数提前做变量化引用                                      | 方便多个用例间的变量传递，调用函数等                              |


## 三、定开级功能

#### 注意：以下功能名称是通用的，但里面的关键字代码逻辑不通用。需要根据自己公司产品的组件，做调整（框架现有的field关键字，编写思路值得参考）

| 功能名称         | 实现原理                                             | 作用                                                                           |
|--------------|--------------------------------------------------|------------------------------------------------------------------------------|
| FieldsMiXin类 | 按字段维度，封装每一种类的字段定位、输入内容/选择选项等操作                   | eg: 把单选下拉框字段封装为一个关键字key_select_field ,关键字包含以下动作：定位字段、单击展开下拉框、下拉选择选项、收起下拉框    |
| LocalMiXin类  | 给FieldsMiXin类，提供多样化定位方法                          | eg: 文本框字段定位，提供多样化方式：1、普通的xpath、id等定位;2、若字段有label，按字段label的text定位；3、其它（可无限扩展） |
| EleAssert类   | 元素断言类，基本原理：定位到需要断言的元素，获取需要断言的信息进行断言，返回True/False | 元素断言                                                                         |
| BaseMiXin类   | KeyWordLib类的拆分，你也可以不拆分                           | 略过                                                                           |

## extra：关键字封装的思路

#### 1、提供给字段的多种定位方式，如：_location_by_name、_location_by_parent、location_by_loc， 灵活支持字段的定位
#### 2、定位到字段后，对字段的子元素进行相应的业务操作（eg：定位到单选下拉框，然后：点击展开，选择目标选项，点击收起下拉）



### PS：注意conftest.py中，钩子函数pytest_sessionstart、pytest_sessionfinish的代码内容，便于调试。



## 全局拓展
### 注入save_png函数：
    在关键字中，可添加定位参数instance=None, 在关键字代码体中的任意位置, 注入save_png函数调用。
![img.png](/assets/save_png.png)

### excel调试模式：
    若想要调试运行一部分步骤，可通过修改步骤id=-999，阻止后续步骤生成test用例。


## Driver驱动
### 1、自动安装并使用(推荐)：
     pip install webdriver_manager -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    ```
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    ```



### 2、手动安装：ChromeDriver驱动仓库（国内最新）
    https://registry.npmmirror.com/binary.html?path=chrome-for-testing
    https://storage.googleapis.com/chrome-for-testing-public/{{ 版本号 }}/win64/chromedriver-win64.zip






