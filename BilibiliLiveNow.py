from lxml import etree
import re
from selenium import webdriver
from selenium import __version__ as seleniumVersion
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
import time
import ujson

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
bilibiliConfigPath = os.path.join(__location__, "config", "bilibili-live")
if not os.path.exists(bilibiliConfigPath):
    os.makedirs(bilibiliConfigPath)

prefs = {"profile.managed_default_content_settings.images": 2, 'permissions.default.stylesheet': 2}
options = webdriver.ChromeOptions()
options.add_experimental_option("prefs", prefs)
options.add_argument("--window-size=1400,600")
options.add_argument("--no-sandbox")
# options.add_argument('--headless')

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

driver.get('https://live.bilibili.com/')
time.sleep(10)


js = 'scrollWin = document.getElementById("app").firstChild'
driver.execute_script(js)
documentHeight = driver.execute_script("return scrollWin.scrollHeight")

documentNewHeight = 0
while documentNewHeight < documentHeight:
    # 向下划动300px，到底，刷出所有的直播间链接
    js = "window.scrollBy(0, 300)"
    driver.execute_script(js)
    time.sleep(5)
    documentNewHeight += 300
    documentHeight = driver.execute_script("return scrollWin.scrollHeight")

unicodeText = driver.page_source

# 通过XPath定位元素并获取文本
html_tree = etree.HTML(unicodeText)
div = html_tree.xpath("//div[@class='room-ctnr w-100']")
anchor_name_list = html_tree.xpath("//div[@class='room-anchor card-text p-relative']/span/text()")
room_id_list_json = html_tree.xpath("//a[@class='dp-block room-card-ctnr p-relative w-100']/@data-bl-report-click")


length = len(anchor_name_list)
base_url = "https://live.bilibili.com/"
for i in range(length):
    room_id = ujson.loads(room_id_list_json[i])["msg"]["room_id"]
    # 原直播间url
    target_url =  base_url + str(room_id)
    driver.get(target_url)
    time.sleep(2)
    # 发生跳转后的url
    final_url = driver.current_url
    final_room_id = final_url.rsplit('/', 1)[-1]
    item = {
        'quality': '标清',
        'url': final_url,
        'name': anchor_name_list[i]
    }

    configPath = os.path.join(bilibiliConfigPath, f'{final_room_id}.json')
    with open(configPath, 'w', encoding='utf-8') as json_file:
        ujson.dump(item, json_file, ensure_ascii=False)

# 关闭浏览器
driver.quit()
