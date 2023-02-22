
from source.setting.urls import urls
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
from selenium.common.exceptions import NoSuchWindowException

urls = urls()
max_wait = 90
max_wait2 = 10
class scrapper():
    def __init__(self, driver):
        self.driver = driver


    def isLoggedin(self):
        self.driver.get(urls.main)

        try:
            element = WebDriverWait(self.driver, max_wait2*2)\
                .until(EC.presence_of_element_located((By.XPATH, '//img[contains(@class, "avatar-img")]')))
            self.driver.find_element_by_xpath('//img[contains(@class, "avatar-img")]')
            self.login_status = True
       
        except NoSuchWindowException as e:
            self.login_status = e

        except:
            self.login_status = False
        finally:
            return self.login_status


    def isUserLoggedin(self, username):
        if self.login_status:
            return str(self.driver.find_element_by_xpath('//input[contains(@id, "usernameInput")]')\
                .get_attribute('value')).lower() == username.lower()
        else:
            return ('Run isloggedin method first')
            

    def login(self, username, password):
        if self.login_status:
            print('Already logged in, run logout method first')
            return self.login_status
        try:
            try:
                register_btn = self.driver.find_element_by_xpath('//a[contains(@class, "login-action")]')
                self.driver.execute_script("arguments[0].click();", register_btn)	
                self.driver.switch_to.frame("loginIframe")
            except:
                pass

            element = WebDriverWait(self.driver, max_wait)\
                .until(EC.presence_of_element_located((By.ID, "username")))
            self.driver.find_element_by_xpath('//input[contains(@id, "username")]')\
                .send_keys(username)
            sleep(1)
            self.driver.find_element_by_xpath('//input[contains(@id, "username")]')\
                .send_keys(Keys.ENTER)

            element = WebDriverWait(self.driver, max_wait)\
                .until(EC.presence_of_element_located((By.ID, "password")))
            self.driver.find_element_by_xpath('//input[contains(@id, "password")]')\
                .send_keys(password)
            sleep(1)
            self.driver.find_element_by_xpath('//input[contains(@id, "password")]')\
                .send_keys(Keys.ENTER)
            
            element = WebDriverWait(self.driver, max_wait2*3)\
                .until(EC.presence_of_element_located((By.XPATH, '//img[contains(@class, "avatar-img")]')))
            
            self.login_status = True
            return self.login_status

        except Exception as e:
            
            traceback.print_exc()
            self.login_status = False
            return self.login_status

    
    def logout(self):
        if self.login_status:
            try:
                profile_btn = self.driver.find_element_by_xpath("//div[contains(@id, 'profileModal')]")
                self.driver.execute_script("arguments[0].click();", profile_btn)

                element = WebDriverWait(self.driver, max_wait)\
                    .until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/signout')]")))
                logout_btn = self.driver.find_element_by_xpath("//a[contains(@href, '/signout')]")
                self.driver.execute_script("arguments[0].click();", logout_btn)
                
                self.login_status = False
                return True

            except Exception as e:
                traceback.print_exc()
                self.login_status = True
                return False
        else:
            return ("already logged out")

    def uploadVideo(self, video_path):
        try:
            
            if self.driver.current_url == urls.formAction:
                try:
                    self.driver.refresh()
                    obj = self.driver.switch_to.alert
                    sleep(2)
                    obj.accept()
                except:
                    pass
            else:
                self.driver.get(urls.formAction)
            # driver.refresh()
            element = WebDriverWait(self.driver, max_wait)\
                .until(EC.presence_of_element_located((By.XPATH, "//button[contains(@id, 'browseButton')]")))
            sleep(5)
            # browse_btn = self.driver.find_element_by_id('browseButton')
            # self.driver.execute_script("arguments[0].click();", browse_btn)
            input_file_video = self.driver.find_element_by_xpath("//input[@type='file']")\
                .send_keys(video_path)
            
            element = WebDriverWait(self.driver, max_wait*3)\
                .until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'ویدیوی شما با موفقیت بارگذاری شد')]")))
            
            self.video_upload = True
            return self.video_upload

        except Exception as e:
            # raise e
            traceback.print_exc()
            print('error in video upload' + str(e))
            self.video_upload = False
            return self.video_upload

    def uploadVideoData(self, image_path, title, description,\
            category, tags, playlist, comments_allowed):
        
        self.video_data_upload = False
        if not self.video_upload:
            return self.video_data_upload
        
        try:
            input_file_img = self.driver.find_element_by_xpath("//input[@name='thumbnail-file']")\
                .send_keys(image_path)
            sleep(1)
            
            input_title = self.driver.find_element_by_xpath("//input[@name='title']")\
                .send_keys(title)

            input_decription = self.driver.find_element_by_xpath("//textarea[@name='descr']")\
                .send_keys(description)
            
            if category != "":
                try:
                    category_option = self.driver.find_element_by_xpath\
                        ("//div[text()='" + category + "']")
                    self.driver.execute_script("arguments[0].click();", category_option)
                except:
                    category_option = self.driver.find_element_by_xpath\
                        ("//div[text()='" + "آموزشی" + "']")
                    self.driver.execute_script("arguments[0].click();", category_option)
                    print('Warning, Category does not exist.' )
            span_tags = self.driver.find_elements_by_xpath("//span[contains(text(), 'انتخاب کنید')]")[0]
            self.driver.execute_script("arguments[0].click();", span_tags)
            input_tags = self.driver.find_elements_by_xpath("//input[contains(@placeholder, 'جستجو')]")[2]
            sleep(0.5)
            
            
            tags_str = '-'.join(tags)
            input_tags.send_keys(tags_str)
            sleep(1)
            element = WebDriverWait(self.driver, max_wait2*3)\
                .until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(text(), 'درحال جستجو')]")))
            sleep(1)
            input_tags.send_keys(Keys.ENTER)
            sleep(0.5)

            span_playlist = self.driver.find_elements_by_xpath("//span[contains(text(), 'انتخاب')]")[3]
            self.driver.execute_script("arguments[0].click();", span_playlist)
            input_playlist = self.driver.find_elements_by_xpath("//input[contains(@placeholder, 'جستجو')]")[3]
            sleep(0.5)

            playlist_main_div = self.driver.find_elements_by_xpath("//div[contains(@class, 'ss-list')]")[2]
            playlist_items_div = playlist_main_div.find_elements_by_xpath("//div[contains(@class, 'ss-option')]")
            
            play_list_exists = False
            if playlist != "":
                if playlist_items_div != "":
                    for item in playlist_items_div:
                        if playlist == item.text:
                            self.driver.execute_script("arguments[0].click();", item)
                            play_list_exists = True
                            break
                
                if not play_list_exists:
                    input_playlist.send_keys(playlist)
                    add_playlist_btn = self.driver.find_elements_by_xpath("//div[contains(@class, 'ss-addable')]")[1]
                    self.driver.execute_script("arguments[0].click();", add_playlist_btn)
        
            post_video_btn = self.driver.find_element_by_xpath("//button[@name='submit']")
            self.driver.execute_script("arguments[0].click();", post_video_btn)

            sleep(10)
            try:
                span_tags = self.driver.find_elements_by_xpath("//label[contains(text(), 'آدرس ویدیو')]")[0]
                self.video_data_upload = True
            except:
                print('final upload approval failed')
            return self.video_data_upload
            
        except Exception as e:
            traceback.print_exc()
            print('error in data video upload ' + str(e))
            self.video_data_upload = False
            return self.video_data_upload

