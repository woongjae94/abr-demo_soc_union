from selenium import webdriver
import pyautogui as pg

W, H = pg.size()
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument("lang=ko_KR")
options.add_experimental_option('excludeSwitches', ['enable-automation'])
browser = webdriver.Chrome(chrome_options=options, executable_path = './chromedriver')
#browser.set_window_position(W//2,0)
#browser.set_window_size(W//2, H)
browser.get('http://google.com')

browser.execute_script('window.open("http://google.com", "_blank");')

tabs = browser.window_handles
browser.switch_to_window(tabs[1])
browser.get('http://google.com')

browser.switch_to_window(tabs[0])


