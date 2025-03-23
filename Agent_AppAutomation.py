"""
This is an app aputomation code that will open an app in android and 
click on an element 

"""
from appium import webdriver
import asyncio
from appium.webdriver.common.appiumby import AppiumBy
from typing import Any, Dict
from appium.options.common import AppiumOptions
from autogen.agentchat import UserProxyAgent, AssistantAgent,register_function


def DesiredCapabilities(): 
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


def OpenClock():

        url,cap = DesiredCapabilities()
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
        
    
async def main():
        
        #define the model to use
        config_list =[
            {
                "model": "gpt-4o",
                "api_key": ""
            }
        ]
        #define the llm config
        llm_config ={
            "timeout": 10,
            "seed": 42,
            "config_list": config_list,
            "temperature": 0   
            }
        
        #define the autogen agents 
        assistant = AssistantAgent(
            name="App_assistant",
            llm_config=llm_config,
        )

        #defienthe Userproxy agent 
        user = UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config={
                    "use_docker": False,
                    "work_dir": "Applogs"
                                  }
        )
         # defining the register functions to make above functions to e detected ny agent 
        #get request
        register_function(
            OpenClock,
            caller=assistant,
            executor=user,  
            name = "open_clock",
            description="this makes call to openclock function and performs the task"
        )

        prompt_task = """
                 Open the Clock app and click the Timer and Alarm buttons, then press the Home button only once.
               """
        await user.initiate_chat(
            assistant,
            message=prompt_task
        )

#run 
if __name__ == '__main__':
    asyncio.run(main())




        

