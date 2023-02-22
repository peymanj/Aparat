from math import trunc
from os.path import isfile
from .clean import clean
from .driver_controller import get_driver
from .scrapper import scrapper as scrapper_class
import datetime
from source.database.database_handler import databaseHandler
import os
from time import sleep
from random import randint, sample
import traceback
from selenium.common.exceptions import NoSuchWindowException
# import ptvsd 

def persian_to_english(string):
    new_string = ''
    persian_numbers = '۰۱۲۳۴۵۶۷۸۹'
    english_numbers  = '0123456789'
    for s in string:
        if s in persian_numbers:
            new_string += english_numbers[persian_numbers.index(s)]
        else:
            new_string += s
    return new_string

class robotInitiator():

    def __init__(self):
        self.exit_flag = False

    def exit_slot(self):
        self.exit_flag = True

    def login_control(self, username, password, driver):
        try:
            scrapper = scrapper_class(driver)
            login_status = scrapper.isLoggedin() 
            if login_status == True:
                if not scrapper.isUserLoggedin(username):
                    print('Switching Accounts.')
                    if scrapper.logout():
                        if scrapper.login(username, password):
                            print('Switch Successful')
                            return True, scrapper
                        else:
                            print('Unable to login after logout.')
                            return False, None
                    else:
                        print('Unable to logout.')
                        return False, None
                else:
                    print('already logged in')
                    return True, scrapper
            elif isinstance(login_status, NoSuchWindowException):
                pass
            else:
                if scrapper.login(username, password):
                    print('Login Successful.')
                    return True, scrapper
                else:
                    print('Unable to login')
                    return False, None
        except Exception as e:
            traceback.print_exc()
            print('Robot run sequesnce failed.' + str(e))
            return False, None

    def run(self, scrapper, video_path, image_path, title, description,\
                    classification, tags, playlist, comments_allowed):
        try:

            if scrapper.uploadVideo(video_path):
                if scrapper.uploadVideoData(image_path, title, description,\
                    classification, tags, playlist, comments_allowed):
                    # exec_timer.cancel()
                    return True
                else:
                    print('unable to upload video data')
                    # exec_timer.cancel()
                    return False
            else:
                print('Unable to load fromAction')
                # exec_timer.cancel()
                return False

            
        except Exception as e:
            traceback.print_exc()
            print(e)
            print('timeout uploading robot')
            # exec_timer.cancel()
            return False
            
    def spec_video_upload_initiate(self, spec_sequence_list, db_handler, driver, send_log_signal, setting ):
        wait_start = setting.wait_min
        wait_end = setting.wait_max
        n_tags = setting.tag_number # min 3
        img_format = setting.cover_pic_format
        cover_image_directory = setting.cover_img_path

        wait_time = randint(wait_start, wait_end)
        ttime=0
        while ttime < wait_time:
            
            if self.exit_flag:
                return

            ttime += 1
            now = datetime.datetime.now()
            for spec_sequence in spec_sequence_list:

                upload_time = datetime.datetime.strptime(persian_to_english(spec_sequence['upload_time']),'%H:%M:%S')
                if upload_time.time() <= now.time() < (upload_time + datetime.timedelta(seconds=250)).time():
                # if True:

                    class_data_list, status  = db_handler.get_class(spec_sequence['name'])
                    class_data = class_data_list[0]
                    classification = class_data['aparat_category']

                    tags = [] 
                    for t in spec_sequence['tag_str'].splitlines():
                        if t.strip() !="":
                            tags.append(t.strip())				
                        else:
                            pass

                    tags =  sample(spec_sequence['tag_str'].splitlines(), min(n_tags, len(tags))) # random tags
                    video_path = spec_sequence['video_path']
                    video_name = os.path.splitext(video_path.split('/')[-1])[0]
                    

                    image_directory = str(os.path.dirname(video_path)) + "/" + cover_image_directory               
                    image_path = image_directory + "/"+ video_name + img_format
                    
                    desc = [] 
                    for s in spec_sequence['description'].split('&'):
                        if s.strip() !="":
                            desc.append(s.strip())				
                        else:
                            pass
                    
                    desc = sample(desc, 1) if desc else ""
                    class_name =  class_data['aparat_category']
                    playlist = spec_sequence['playlist_name']
                    comments_allowed = True

                    queryset, status = db_handler.get_spec_video_status(video_path, class_data['name'], str(upload_time.time()))
                    uploaded = bool(int(queryset[0]["status"]))
                    if uploaded:
                        db_handler.set_spec_upload_status(class_data['name'], video_path, str(upload_time.time()), int(upload_status))
                        continue
                    
                    username = class_data['username']
                    password = class_data['password']

                    status, scrapper = self.login_control(username, password, driver)
                    if not status:
                        print('login failed')
                        continue

                    upload_status = True
                    upload_status = self.run(scrapper, video_path, image_path, video_name, desc, class_name, tags, playlist, comments_allowed)
                    

                    if upload_status:
                        db_handler.set_spec_upload_status(class_data['name'], video_path, str(upload_time.time()), int(upload_status))
                    log = {'video_name': video_path, 'class_name': class_data['name'], 'upload_time': datetime.datetime.now(), 'status': int(upload_status)}
                    send_log_signal.emit(log)
            sleep (1)

    def initiate(self, sequence_list, spec_sequence_list, send_log_signal, setting,\
         finished_signal, finished_with_error_signal):
        # ptvsd.debug_this_thread()
        wait_start = setting.wait_min
        wait_end = setting.wait_max
        n_tags = setting.tag_number # min 3
        img_format = setting.cover_pic_format
        cover_image_directory = setting.cover_img_path

        if not setting.multi_instance:
            clean('chrome')
        
        driver = self.create_driver(setting)
        if str == type(driver):
            finished_with_error_signal.emit(driver)
            finished_signal.emit()
            return
        

        db_handler = databaseHandler()
        
        while True:
            for sequence in sequence_list:

                try:
                    class_name = sequence['name']
                    start_time = sequence['start_time']
                    end_time = sequence['end_time']
                    max_number_of_uploads_per_seq = sequence['video_count']

                    start_value = datetime.datetime.strptime(persian_to_english(start_time),'%H:%M:%S').time()
                    end_value = datetime.datetime.strptime(persian_to_english(end_time),'%H:%M:%S').time()
                    now = datetime.datetime.now().time()
                    if start_value > now  or now >= end_value: 
                        continue

                    class_data_list, status  = db_handler.get_class(class_name)
                    class_data = class_data_list[0]
                    
                    username = class_data['username']
                    password = class_data['password']
                    
                    status, scrapper = self.login_control(username, password, driver)
                    if not status:
                        break



                    description_list, status  = db_handler.get_descriptions(class_name)
                    random_description = description_list[randint(0, len(description_list)-1)]['name']
                    video_path = class_data['folder_path']
                    image_path = video_path.replace('\\','/') + '/' + cover_image_directory
                    tag_data, status  = db_handler.get_tags(class_name)
                    tags = sample([tag['name'] for tag in tag_data], min(n_tags, len(tag_data))) # random tags

                    description = random_description
                    classification = class_data['aparat_category']
                    playlist = class_data['playlist_name']

                    comments_allowed = True
                    
                    number_of_videos_uploaded_in_seq = 0
                    now = datetime.datetime.now().time()
                    
                    while number_of_videos_uploaded_in_seq < max_number_of_uploads_per_seq\
                        and now < end_value:    
                        scanned_path = os.scandir(video_path) # Scanning PDF folder for existing files.
                        video_count = 0
                        for video_file in scanned_path:
                            if isfile(video_file):
                                video_count += 1

                        scanned_path = os.scandir(video_path) 
                        for video_file in scanned_path:
                            video_list_data, status  = db_handler.get_upload_temp(class_name)                        
                            if video_list_data:
                                video_name_list = [video['video_name'] for video in video_list_data] 
                            else:
                                video_name_list = []

                            
                            if video_count <= len(video_name_list):
                                db_handler.reset_upload_temp(class_name)
                                continue


                            now = datetime.datetime.now().time()
                            if now>=end_value or number_of_videos_uploaded_in_seq >= max_number_of_uploads_per_seq:
                                break
                        
                            if isfile(video_file):
                                video_name = video_file.name
                                db_video_path = video_file.path
                                if video_name in video_name_list:
                                    # db_handler.delete_upload_temp(class_name, video_name)
                                    continue

                                title = ''
                                title_list, status = db_handler.get_titles(db_video_path)
                                if title_list:
                                    title = title_list[randint(0, len(title_list) - 1)]['title']
                                if not title:
                                    title = os.path.splitext(video_name)[0]
                                image_name = os.path.splitext(video_name)[0] + img_format

                                upload_status = True
                                upload_status = self.run(scrapper, os.path.join(video_path, video_name),\
                                (image_path +"/"+ image_name), title, description, classification, tags, playlist, comments_allowed)
                                if upload_status:
                                    number_of_videos_uploaded_in_seq += 1
                                db_handler.set_upload_temp(class_name, video_name)
                                log = {'video_name': video_name, 'class_name': class_name, 'upload_time': datetime.datetime.now(), 'status': int(upload_status)}
                                
                                send_log_signal.emit(log)
                            if self.exit_flag:
                                finished_signal.emit()
                                driver.close()
                                return
                            
                            # ----- special video loop:
                            self.spec_video_upload_initiate(spec_sequence_list, db_handler, driver, send_log_signal, setting)

                    sequence_list.remove(sequence)
                except Exception as e:
                    traceback.print_exc()
                    print('Robot initialtion failed.' + str(e))
                    # raise e
                    try:
                        driver.close()
                    except:
                        pass
                    return False

            # running spec upload --- 
            if sequence_list == []:
                self.spec_video_upload_initiate(spec_sequence_list, db_handler, driver, send_log_signal, setting)

            if self.exit_flag:
                try:
                    driver.close()
                except Exception as e:
                    traceback.print_exc()
                    print(e)
                    pass
                sleep(5)
                finished_signal.emit()
                return

            sleep(5)


    def create_driver(self, setting):
        return get_driver('chrome', setting.show_browser)
            
