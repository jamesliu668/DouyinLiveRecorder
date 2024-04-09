from lxml import etree

from selenium import webdriver
from selenium import __version__ as seleniumVersion
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
import time
import ujson

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
dyConfigPath = os.path.join(__location__, "config", "dy-live")


prefs = {"profile.managed_default_content_settings.images": 2, 'permissions.default.stylesheet': 2}
options = webdriver.ChromeOptions()
options.add_experimental_option("prefs", prefs)
options.add_argument("--start-maximized")  # 将浏览器窗口最大化
options.add_argument("--no-sandbox")
options.add_argument('--headless')

# 在Linux和Mac中如果chrome或者chromium已经使用yum或者brew安装在系统路径上就不需要配置
chromeBinaryLocation = os.path.join("/usr/local/bin/chromium") #打包配置
options.binary_location = chromeBinaryLocation

# 在Linux和Mac中如果chromedriver已经使用yum或者brew安装在系统路径上就不需要配置，使用chromedriver -version查看版本
# consider using webdriver_manager, see https://stackoverflow.com/questions/63421086/modulenotfounderror-no-module-named-webdriver-manager-error-even-after-instal
chromeDrivePath = os.path.join(__location__, 'chrome', 'chromedriver') #打包配置

if int(seleniumVersion.split('.')[0]) > 3:
    # in selenium 4
    # https://stackoverflow.com/questions/64717302/deprecationwarning-executable-path-has-been-deprecated-selenium-python
    service = Service(executable_path=chromeDrivePath)    
    driver = webdriver.Chrome(service=service, options=options)
else:
    driver = webdriver.Chrome(executable_path=chromeDrivePath, chrome_options=options)

# 打开网页
driver.set_page_load_timeout(50)
wait = WebDriverWait(driver, 5)

driver.get('https://live.douyin.com/')
time.sleep(1.2)
unicodeText = driver.page_source

# 通过XPath定位元素并获取文本
html_tree = etree.HTML(unicodeText)
hrefs = html_tree.xpath("//div[@class='gnejI3bf']")

url_list = hrefs[0].xpath('./a/@href')
anchor_name = hrefs[0].xpath('.//object//text()')
length = len(anchor_name)

for i in range(length):
    item = {
        'quality': '标清',
        'url': url_list[i],
        'name': anchor_name[i]
    }
    configPath = os.path.join(dyConfigPath, f'{anchor_name[i]}.json')
    with open(configPath, 'w', encoding='utf-8') as json_file:
        ujson.dump(item, json_file, ensure_ascii=False)
# 关闭浏览器
driver.quit()
