"""
This is an app aputomation code that will open an app in android and 
click on an element 

"""
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from typing import Any, Dict
from appium.options.common import AppiumOptions
import asyncio

class Automation:

    @classmethod
    def DesiredCapabilities(cls):
        #define the desired capabilities
        cap:Dict[str, Any]={
            'platformName': 'Android',
            'deviceName': 'emulator-5554',
            'app': '',  # Leave empty since the app is preinstalled
            'automationName': 'UiAutomator2',
            'appPackage': 'com.google.android.deskclock',
            'appActivity': 'com.android.deskclock.DeskClock'
        }
        url = 'http://127.0.0.1:4723'
        return url, cap


    def OpenClock(self):
        url,cap = self.DesiredCapabilities()
    # initilize the Appium Driver
        driver = webdriver.Remote(url,options=AppiumOptions().load_capabilities(cap))

        try:
            #lets wait for the app to open
            driver.implicitly_wait(10)

            timer_elemet = driver.find_element(by=AppiumBy.XPATH, value='//rk[@content-desc="Timer"]')
            timer_elemet.click()
            driver.implicitly_wait(5)
            print("Timer button clicked!")
            alarm_element = driver.find_element(by=AppiumBy.XPATH, value='//rk[@content-desc="Alarm"]')
            alarm_element.click()
            print("Alarm button clicked!")

            # go to home
            driver.press_keycode(3)
            print("home button pressed")

        except Exception as a:  
            print(f'An error occurred{a}')

        finally:
            #quit the session 
            driver.quit()
    
    async def main(self) -> None:
        self.OpenClock() #call the function 

#run 
if __name__ == '__main__':
    automation = Automation()
    asyncio.run(automation.main())


        

