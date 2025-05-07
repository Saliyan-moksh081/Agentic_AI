from autogen.agentchat import UserProxyAgent, AssistantAgent,register_function
from appium.webdriver.common.appiumby import AppiumBy
from appium import webdriver
import openai
from dotenv import load_dotenv
import os
from appium.options.common import AppiumOptions

load_dotenv()
# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize AutoGen agents
assistant = AssistantAgent("assistant", llm_config={"config_list": [{"model": "gpt-4o"}]})
user = UserProxyAgent(
     name="user", 
     human_input_mode="NEVER",
     code_execution_config={
                    "use_docker": False,
                    "work_dir": "Applogs"
                 }
     )

# Appium desired capabilities (Android example)
desired_caps = {
     'platformName': 'Android',
     'deviceName': 'emulator-5554',
     'app': '',  # Leave empty since the app is preinstalled
     'automationName': 'UiAutomator2',
     'appPackage': 'in.redbus.android',
     'appActivity': 'in.redbus.android.root.SplashScreen',
     'noReset': True,  # Don't reset app state
     'fullReset': False,  # Don't uninstall the app
     'autoGrantPermissions': True,  # Grant all permissions automatically
}

driver = webdriver.Remote("http://localhost:4723",options=AppiumOptions().load_capabilities(desired_caps))

def find_element_adaptive(element_name: str):
    """Self-healing locator using LLM to find elements."""
    try:
        return driver.find_element("id", f"com.example.app:id/{element_name}")
    except:
        # Ask LLM for fallback locators if ID fails
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{
                "role": "user", 
                "content": f"Suggest alternative XPath for {element_name} in a mobile login screen."
            }]
        )
        xpath = response.choices[0].message.content
        return driver.find_element("xpath", xpath)

def Onboardscreen():
     try:
            appStart = driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value='Predicted app: redBus')
            appStart.click()

            # popup_closebtn = find_element_adaptive("popup_close")
            metro_lobBtn = find_element_adaptive("metro_icon")
            city_select = find_element_adaptive("city_select")

            # popup_closebtn.click()
            driver.implicitly_wait(5)
            metro_lobBtn.click()
            city_select.click()
            
     except Exception as a:  
          return f'Metro flow failed{a}'
            
# Register the test function with AutoGen
register_function(
    Onboardscreen,
    caller=assistant, 
    executor=user,  
    name = "MetroOnboard",
    description="this will perform all the tasks on the metro onbaord screen",
)

# Start the test
user.initiate_chat(
    assistant,
    message="Click on the close button on the pop up and click on the metro icon in the app header"
)

driver.quit()