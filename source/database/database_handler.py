from .database_tools import databaseController
import os
from source.setting.DBConfig import CONFIG
from datetime import date, datetime


class databaseHandler():

    def __init__(self):
        mode, db_path = self.db_check()
        self.db_handler = databaseController(db_path)
        self.db_path = db_path
        if mode == 'create':
            self.create_db()
        self.alter_db()

    def db_check(self):
        wd = os.getcwd() # creating new DB if not exists.
        db_path = os.path.join(wd, CONFIG['db_path'])
        if os.path.isfile(db_path):
            return None, db_path
        else:
            return 'create', db_path

    def create_db(self):
        try:	
            video_classes_create = """ CREATE TABLE IF NOT EXISTS video_classes (
                id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                name text NOT NULL,
                folder_path text NOT NULL,
                playlist_name text NOT NULL,
                aparat_category text NOT NULL,
                active int DEFAULT 0 NOT NULL,
                username text NOT NULL,
                password text NOT NULL,
                UNIQUE(name)
            );
            """
            self.db_handler.run_sql(video_classes_create)

            log_table_create = """ CREATE TABLE IF NOT EXISTS log (
                id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                file_name text NOT NULL,
                class_name text NOT NULL,
                upload_date datetime NOT NULL,
                upload_status bit NOT NULL
            );
            """ 
            self.db_handler.run_sql(log_table_create)

            tags_create = """ CREATE TABLE IF NOT EXISTS tags(
                id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                class_id integer NOT NULL,
                name text NOT NULL,
                FOREIGN KEY(class_id) REFERENCES video_classes(id) ON DELETE CASCADE
                UNIQUE(class_id, name)
            );
            """
            self.db_handler.run_sql(tags_create)

            descriptions_create = """ CREATE TABLE IF NOT EXISTS descriptions(
                id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                class_id integer NOT NULL,
                name text NOT NULL,
                FOREIGN KEY(class_id) REFERENCES video_classes(id) ON DELETE CASCADE
                UNIQUE(class_id, name)
            );
            """
            self.db_handler.run_sql(descriptions_create)

            profiles_create = """ CREATE TABLE IF NOT EXISTS profiles(
                id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                name text NOT NULL,
                date datetime NOT NULL,
                UNIQUE(name),
                UNIQUE(date)
            );
            """
            self.db_handler.run_sql(profiles_create)

            sequence_create = """ CREATE TABLE IF NOT EXISTS sequence(
                id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                profile_id integer NOT NULL,
                class_id Integet NOT NULL,
                start_time text NOT NULL,
                end_time text NOT NULL,
                video_count int NOT NULL DEFAULT 1,
                FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
                FOREIGN KEY(class_id) REFERENCES video_classes(id) ON DELETE CASCADE
            );
            """
            self.db_handler.run_sql(sequence_create)

            upload_temp_create = """ CREATE TABLE IF NOT EXISTS upload_temp(
                class_id Integer NOT NULL,
                video_name text NOT NULL,
                FOREIGN KEY(class_id) REFERENCES video_classes(id) ON DELETE CASCADE
            );
            """
            self.db_handler.run_sql(upload_temp_create)

            spec_videos_create = """ CREATE TABLE "spec_videos" (
                "id"	integer NOT NULL,
                "class_id"	integer NOT NULL,
                "video_path"	text NOT NULL,
                "description"	text NOT NULL,
                "tag_str"	text NOT NULL,
                "upload_time"	text NOT NULL,
                "status"	bit DEFAULT 0,
                PRIMARY KEY("id" AUTOINCREMENT),
                FOREIGN KEY("class_id") REFERENCES "video_classes"("id") ON DELETE CASCADE
            );
            """
            self.db_handler.run_sql(spec_videos_create)

            setting_create = """ CREATE TABLE "setting" (
                "id" integer NOT NULL,
                "img_path" text NOT NULL,
                "cover_pic_format"	text NOT NULL,
                "tag_number" integer NOT NULL,
                "show_browser" bit NOT NULL,
                "wait_min"	integer NOT NULL,
                "wait_max" integer NOT NULL,
                "multi_instance" bit NOT NULL
            );
            """
            self.db_handler.run_sql(setting_create)

            initiate_setting = """INSERT INTO setting(id, img_path, cover_pic_format, tag_number,
                show_browser, wait_min, wait_max, multi_instance) VALUES (1, 'images', '.png', 3, 0, 2, 10, 0);
            """
            self.db_handler.run_sql(initiate_setting)

            users_create = """ CREATE TABLE "users" (
                "id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                "user" text NOT NULL,
                "pass"	text NOT NULL,
                "access" text NOT NULL DEFAULT 'main_admin',
                UNIQUE(user)
            );
            """
            self.db_handler.run_sql(users_create)

            initiate_user = """INSERT INTO users(user, pass, access) VALUES ("main_admin", 
            "ddf55f1bf1e2edf05232e268211f9bcd", 'main_admin');
            """  # 123450
            self.db_handler.run_sql(initiate_user)

            initiate_user = """INSERT INTO users(user, pass, access) VALUES ("superuser", 
            "0b0e535c41daec1df717559f73744fc1", "superuser");
            """  # 
            self.db_handler.run_sql(initiate_user)
            
            return True

        except Exception as e:
            print('Error in connecting to or creating DB' + str(e))
            return False

    def alter_db(self):
        query = """ALTER TABLE "setting" ADD COLUMN "multi_instance" bit"""
        self.db_handler.run_sql(query)

        query = """
            CREATE TABLE IF NOT EXISTS "video_title" (
                "id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                "video_path" text NOT NULL,
                "title"	text NOT NULL
            );
        """
        self.db_handler.run_sql(query)

    def add_class(self, values):
        try:
            sql = """ INSERT INTO video_classes(
                name, folder_path, playlist_name,
                aparat_category, username, password) values(?,?,?,?,?,?);
            """
            queryset, status = self.db_handler.run_sql(sql, values=values)

        except Exception as e:
            print('Unable to add class to db ' + str(e))
            status = False
            
        finally:
            return queryset, status
  
    def add_log(self, log):
        queryset = None
        try:
            sql = """ INSERT INTO log(
                file_name, class_name, upload_date, upload_status) values(?, ?, ?, ?);
            """
            queryset, status = self.db_handler.run_sql(sql, values=[log['video_name'],\
                 log['class_name'], log['upload_time'], log['status']])

        except Exception as e:
            print('Unable to add log to db ' + str(e))
            status = False
        finally:
            return queryset, status

    def get_log(self, start_date, end_date):
        queryset = None
        try:
            sql = """ SELECT file_name, class_name, upload_date, upload_status FROM log 
                WHERE upload_date BETWEEN Datetime(?) AND Datetime(?) 
                ORDER BY upload_date DESC;
            """
            queryset, status = self.db_handler.run_sql(sql, values=[start_date, end_date])

        except Exception as e:
            print('Unable to get log from db ' + str(e))
            status = False
            
        finally:
            return queryset, status

    def get_classes(self):
        try:
            sql = """ SELECT * FROM video_classes
            """
            queryset, status = self.db_handler.run_sql(sql)

        except Exception as e:
            print('Unable to get classes' + str(e))
            status = False
            
        finally:
            return queryset, status

    def get_class(self, name):
        queryset = None
        try:
            sql = """ SELECT * FROM video_classes WHERE name= ?
            """
            queryset, status = self.db_handler.run_sql(sql, [name])

        except Exception as e:
            print('Unable to get class' + str(e))
            status = False
            
        finally:
            return queryset, status

    def update_class(self, values, name):
     
        try:
            sql = """ UPDATE video_classes SET name=?, folder_path=?, playlist_name=?,
             aparat_category=?, username=?, password=? WHERE name=?;
            """
            queryset, status = self.db_handler.run_sql(sql, values=values+[name])

        except Exception as e:
            print('Unable to update class' + str(e))
            status = False
            
        finally:
            return queryset, status

    def set_class_active_status(self, status, name):
        try:
            sql = """ UPDATE video_classes SET  active=?  WHERE name=?;
            """
            queryset, status = self.db_handler.run_sql(sql, values=[status, name])

        except Exception as e:
            print('Unable to update class active status' + str(e))
            status = False
            
        finally:
            return queryset, status

    def get_class_active_status(self, name):
        try:
            sql = """ SELECT active FROM video_classes WHERE name=?;
            """
            queryset, status = self.db_handler.run_sql(sql, values=[name])

        except Exception as e:
            print('Unable to get class active status ' + str(e))
            status = False
            
        finally:
            return queryset, status

    def get_tags(self, name):
        try: 
            sql = """ SELECT * FROM tags WHERE class_id=(SELECT id FROM video_classes WHERE name=?)
            """
            queryset, status = self.db_handler.run_sql(sql, values=[name])

        except Exception as e:
            print('Unable to get tags ' + str(e))
            status = False
            
        finally:
            return queryset, status

    def set_tags(self, old_tag_list, tag_list, name):
        queryset = None
        status = True

        try: 
            for tag in old_tag_list:
                sql = """ DELETE FROM tags WHERE class_id=(SELECT id FROM video_classes WHERE name=?) AND name=?"""
                queryset, status = self.db_handler.run_sql(sql, values=[name, tag])
            for tag in tag_list:
                sql = """ INSERT INTO tags (class_id, name) VALUES ((SELECT id FROM video_classes WHERE name=?),?)"""
                queryset, status = self.db_handler.run_sql(sql, values=[name, tag])

        except Exception as e:
            print('Unable to set tags ' + str(e))
            status = False
            
        finally:
            return queryset, status

    def get_profiles(self):
            try: 
                sql = """ SELECT * FROM profiles
                """
                queryset, status = self.db_handler.run_sql(sql)

            except Exception as e:
                print('Unable to get profiles ' + str(e))
                status = False
                
            finally:
                return queryset, status

    def get_profile_date(self, name):
        try: 
            sql = """ SELECT date FROM profiles where name = ?
            """
            queryset, status = self.db_handler.run_sql(sql, values=[name])

        except Exception as e:
            print('Unable to get profiles ' + str(e))
            status = False
            
        finally:
            return queryset, status            
    
    def get_profile_by_date(self, date):
            try: 
                sql = """ SELECT * FROM profiles Where date=?
                """
                queryset, status = self.db_handler.run_sql(sql, values=[date])

            except Exception as e:
                print('Unable to get profiles ' + str(e))
                status = False
                
            finally:
                return queryset, status

    def add_profile(self, name, date):
        try:
            sql = """ INSERT INTO profiles(name, date) values(?, ?);
            """
            queryset, status = self.db_handler.run_sql(sql, values=[name, date])

        except Exception as e:
            print('Unable to add profile to db ' + str(e))
            status = False
            
        finally:
            return queryset, status

    def get_active_classes(self):
        try:
            sql = """ SELECT * FROM video_classes WHERE active=1;
            """
            queryset, status = self.db_handler.run_sql(sql)

        except Exception as e:
            print('Unable to add profile to db ' + str(e))
            status = False
            
        finally:
            return queryset, status
    
    def add_sequence(self, profile_name, class_name, start, end, video_count):
        try:
            sql = """ INSERT INTO sequence(profile_id, class_id, start_time, end_time, video_count)  values(
                (SELECT id FROM profiles WHERE name=?),
                (SELECT id FROM video_classes WHERE name=?),
                ?,?,?);
            """
            queryset, status = self.db_handler.run_sql(sql, values=[profile_name, class_name, start, end, video_count])

        except Exception as e:
            print('Unable to add sequence to db ' + str(e))
            status = False
            
        finally:
            return queryset, status

    def get_sequence(self, profile_name):
        try:
            sql = """ SELECT video_classes.name, sequence.start_time, sequence.end_time , sequence.video_count
            FROM (  
                sequence
            JOIN profiles ON sequence.profile_id = profiles.id 
            JOIN video_classes ON sequence.class_id = video_classes.id 
            ) 
            WHERE profiles.id = (SELECT id FROM profiles WHERE name=?) ORDER BY sequence.start_time ASC;
            """
            queryset, status = self.db_handler.run_sql(sql, values=[profile_name])

        except Exception as e:
            print('Unable to add sequence to db ' + str(e))
            status = False
            
        finally:
            return queryset, status

    def delete_sequence(self, profile_name, class_name, start_time):
        
        try:
            sql = """ DELETE FROM sequence WHERE class_id=(SELECT id FROM video_classes WHERE name=?) AND 
            profile_id=(SELECT id FROM profiles WHERE name=?) AND 
            start_time=?"""
            queryset, status = self.db_handler.run_sql(sql, values=[class_name, profile_name, start_time])
        
        except Exception as e:
            print('Unable to delete sequence from db ' + str(e))
            status = False
            
        finally:
            return queryset, status

    def get_descriptions(self, name):
        try: 
            sql = """ SELECT * FROM descriptions WHERE class_id=(SELECT id FROM video_classes WHERE name=?)
            """
            queryset, status = self.db_handler.run_sql(sql, values=[name])

        except Exception as e:
            print('Unable to get descriptions ' + str(e))
            status = False
            
        finally:
            return queryset, status
    
    def set_descriptions(self, old_desc_list, desc_list, name):
        queryset = None
        status = True

        try: 
            for tag in old_desc_list:
                sql = """ DELETE FROM descriptions WHERE class_id=(SELECT id FROM video_classes WHERE name=?) AND name=?"""
                queryset, status = self.db_handler.run_sql(sql, values=[name, tag])
            for tag in desc_list:
                sql = """ INSERT INTO descriptions (class_id, name) VALUES ((SELECT id FROM video_classes WHERE name=?),?)"""
                queryset, status = self.db_handler.run_sql(sql, values=[name, tag])

        except Exception as e:
            print('Unable to set descriptions ' + str(e))
            status = False
            
        finally:
            return queryset, status

    def set_upload_temp(self, class_name, video_name):
        queryset = None
        status = True

        try: 
            sql = """ INSERT INTO upload_temp (class_id, video_name) VALUES ((SELECT id FROM video_classes WHERE name=?),?)"""
            queryset, status = self.db_handler.run_sql(sql, values=[class_name, video_name])

        except Exception as e:
            print('Unable to save upload temp data ' + str(e))
            status = False
            
        finally:
            return queryset, status 

    def get_upload_temp(self, name):
        try: 
            sql = """ SELECT upload_temp.video_name FROM (upload_temp INNER JOIN video_classes ON 
            upload_temp.class_id = video_classes.id) WHERE video_classes.name=?;
            """
            queryset, status = self.db_handler.run_sql(sql, values=[name])

        except Exception as e:
            print('Unable to get upload temp data' + str(e))
            status = False
            
        finally:
            return queryset, status

    def delete_upload_temp(self, class_name, video_name):
        queryset = None
        status = True

        try: 
            sql = """ DELETE FROM upload_temp WHERE class_id =(SELECT id FROM video_classes WHERE name=?) AND video_name=?"""
            queryset, status = self.db_handler.run_sql(sql, values=[class_name, video_name])

        except Exception as e:
            print('Unable to delete from temp data ' + str(e))
            status = False
            
        finally:
            return queryset, status 

    def reset_upload_temp(self, class_name):
        queryset = None
        status = True

        try: 
            sql = """ DELETE FROM upload_temp WHERE class_id =(SELECT id FROM video_classes WHERE name=?)"""
            queryset, status = self.db_handler.run_sql(sql, values=[class_name])

        except Exception as e:
            print('Unable to reset temp data ' + str(e))
            status = False
            
        finally:
            return queryset, status 



    def set_spec_video_sequence(self, file_path, class_name, tags_str, desc_str, time):
        queryset = None
        status = True
        try: 
            sql = """ INSERT INTO spec_videos (class_id, video_path, description, tag_str, upload_time)
             VALUES ((SELECT id FROM video_classes WHERE name=?),?,?,?,?)"""
            queryset, status = self.db_handler.run_sql(sql, values=[class_name, file_path, desc_str, tags_str, time])

        except Exception as e:
            print('Unable to save upload temp data ' + str(e))
            status = False
            
        finally:
            return queryset, status 

    def get_spec_video_sequence(self):
        queryset = None
        status = True
        try: 
            sql = """ SELECT spec_videos.video_path, video_classes.name, spec_videos.tag_str,
            spec_videos.description, spec_videos.upload_time, video_classes.playlist_name, spec_videos.status FROM spec_videos JOIN video_classes 
            ON spec_videos.class_id=video_classes.id ORDER BY spec_videos.upload_time ASC
            """
            queryset, status = self.db_handler.run_sql(sql)

        except Exception as e:
            print('Unable to get spec video sequence data ' + str(e))
            status = False
            
        finally:
            return queryset, status 
    
    def update_spec_sequence(self, video_path_old, class_name_old, upload_time_old, \
        video_path, class_name, upload_time, spec_tags_str, spec_desc_str):
        queryset = None
        status = True
        try: 
            sql = """ UPDATE spec_videos SET class_id=(SELECT id FROM video_classes WHERE name=?),
            video_path = ?,
            description = ?,
            tag_str = ?,
            upload_time = ?
            WHERE video_path=? AND class_id=(SELECT id FROM video_classes WHERE name=?) 
            AND upload_time = ?
            """
            queryset, status = self.db_handler.run_sql(sql, values=[class_name, video_path,\
                spec_desc_str, spec_tags_str, upload_time,\
                video_path_old, class_name_old, upload_time_old ])

        except Exception as e:
            print('Unable to update spec sequence data ' + str(e))
            status = False
            
        finally:
            return queryset, status 

    def delete_spec_sequence(self, file_path, class_name, time):
        queryset = None
        status = True
        try: 
            sql = """ DELETE FROM spec_videos WHERE video_path =? AND class_id=(SELECT id FROM video_classes WHERE name=?) 
            AND upload_time=?
            """
            queryset, status = self.db_handler.run_sql(sql, values=[file_path, class_name, time ])

        except Exception as e:
            print('Unable to delete spec sequence data ' + str(e))
            status = False
            
        finally:
            return queryset, status 

    def set_spec_upload_status(self, class_name, video_path, upload_time, upload_status):
        queryset = None
        status = True
        try: 
            sql = """ UPDATE spec_videos SET status=? 
             WHERE class_id=(SELECT id FROM video_classes WHERE name=?) and video_path=? AND upload_time=?"""
            queryset, status = self.db_handler.run_sql(sql, values=[upload_status, class_name, video_path, upload_time])

        except Exception as e:
            print('Unable to update status data ' + str(e))
            status = False
            
        finally:
            return queryset, status 

    def get_spec_video_status(self, video_path, class_name, upload_time):
        queryset = None
        status = True
        try: 
            sql = """ SELECT status FROM spec_videos 
            WHERE video_path=? AND class_id=(SELECT id FROM video_classes WHERE name=?) 
            AND upload_time = ?
            """
            queryset, status = self.db_handler.run_sql(sql, values=[video_path, class_name, upload_time])

        except Exception as e:
            print('Unable to update spec sequence data ' + str(e))
            status = False
            
        finally:
            return queryset, status 

    def set_spec_upload_status_all(self, upload_status):
        queryset = None
        status = True
        try: 
            sql = """ UPDATE spec_videos SET status=? """
            queryset, status = self.db_handler.run_sql(sql, values=[upload_status])

        except Exception as e:
            print('Unable to update status data ' + str(e))
            status = False
            
        finally:
            return queryset, status 

    def save_setting(self, img_path, cover_pic_format, tag_number,
                 show_browser, wait_min, wait_max, multi_instance):
        queryset = None
        status = True
        try: 
            sql = """ SELECT * FROM setting WHERE id=1"""
            queryset, status = self.db_handler.run_sql(sql)

            if queryset == []:
                sql = """ INSERT INTO setting(id, img_path, cover_pic_format, tag_number,
                 show_browser, wait_min, wait_max, multi_instance) VALUES (1, ?, ?, ?, ?, ?, ?, ?)"""
            else:
                sql = """ UPDATE setting SET img_path=?, cover_pic_format=?, tag_number=?,
                 show_browser=?, wait_min=?, wait_max=?, multi_instance=? WHERE id=1"""
            
            queryset, status = self.db_handler.run_sql(sql, values=[ img_path, cover_pic_format, tag_number,
                 show_browser, wait_min, wait_max, multi_instance])


        except Exception as e:
            print('Unable to update setting data ' + str(e))
            status = False
            
        finally:
            return queryset, status 

    def get_setting(self):
        queryset = None
        status = True
        try: 
            sql = """ SELECT * FROM setting WHERE id=1"""
            queryset, status = self.db_handler.run_sql(sql)

        except Exception as e:
            print('Unable to update setting data ' + str(e))
            status = False
            
        finally:
            return queryset, status
    
    def delete_profile(self, name):
        queryset = None
        status = True
        try: 
            sql = """ DELETE FROM profiles WHERE name=?"""
            queryset, status = self.db_handler.run_sql(sql, values=[name])

        except Exception as e:
            print('Unable to delete profile ' + str(e))
            status = False
            
        finally:
            return queryset, status

    def delete_class(self, name):
        queryset = None
        status = True
        try: 
            sql = """ DELETE FROM video_classes WHERE name=?"""
            queryset, status = self.db_handler.run_sql(sql, values=[name])

        except Exception as e:
            print('Unable to delete class ' + str(e))
            status = False
            
        finally:
            return queryset, status
    
    def update_profile(self, old_name, new_name, date):
        queryset = None
        status = True
        try: 
            sql = """ UPDATE profiles SET name=?, date=? WHERE name=?"""
            queryset, status = self.db_handler.run_sql(sql, values=[new_name, date, old_name])

        except Exception as e:
            print('Unable to update profile ' + str(e))
            status = False
            
        finally:
            return queryset, status

    def login(self, user, password):
        queryset = None
        status = True
        try: 
            sql = """ SELECT * FROM users WHERE user=? AND pass=?"""
            queryset, status = self.db_handler.run_sql(sql, values=[user, password])

        except Exception as e:
            print('Unable to login ' + str(e))
            status = False
            
        finally:
            return queryset, status

    def update_current_user(self, user, old_pass, new_pass):
        try: 
            sql = """ SELECT * FROM users WHERE user=? AND pass=?
            """
            queryset, status = self.db_handler.run_sql(sql, values=[user, old_pass])

            sql = """ UPDATE users SET pass=?
            WHERE user=? AND pass=?
            """
            self.db_handler.run_sql(sql, values=[new_pass, user, old_pass])

        except Exception as e:
            print('Unable to update user data ' + str(e))
            status = False
            
        finally:
            return queryset, status 

    def update_other_user(self, user, new_pass):
        try: 
            sql = """ SELECT * FROM users WHERE user=?
            """
            queryset, status = self.db_handler.run_sql(sql, values=[user])

            sql = """ UPDATE users SET pass=?
            WHERE user=?
            """
            self.db_handler.run_sql(sql, values=[new_pass, user])

        except Exception as e:
            print('Unable to update user data ' + str(e))
            status = False
            
        finally:
            return queryset, status 

    def get_users(self, user_access_list):
        queryset = None
        status = True
        try: 
            sql = """ SELECT id, user, access FROM users WHERE access IN (""" + "?, "*(len(user_access_list)-1) + "?)"
            queryset, status = self.db_handler.run_sql(sql, values=user_access_list)

        except Exception as e:
            print('Unable get users ' + str(e))
            status = False
            
        finally:
            return queryset, status

    def get_user_by_name(self, username):
        queryset = None
        status = True
        try: 
            sql = """ SELECT id, user, access FROM users WHERE user=?"""
            queryset, status = self.db_handler.run_sql(sql, values=[username])

        except Exception as e:
            print('Unable get user ' + str(e))
            status = False
            
        finally:
            return queryset, status
    
    def delete_user(self, username):
        queryset = None
        status = True
        try: 
            sql = """ DELETE FROM users WHERE user =?"""
            queryset, status = self.db_handler.run_sql(sql, values=[username])

        except Exception as e:
            print('Unable to delete user ' + str(e))
            status = False
            
        finally:
            return queryset, status 

    def add_user(self, username, password, access):
        queryset = None
        status = True
        try: 
            sql = """ INSERT INTO users (user, pass, access) VALUES (?,?,?)"""
            queryset, status = self.db_handler.run_sql(sql, values=[username, password, access])

        except Exception as e:
            print('Unable to add user ' + str(e))
            status = False
            
        finally:
            return queryset, status

    def get_titles(self, video_path):
        try:
            sql = """ SELECT * FROM video_title WHERE video_path = ?
            """
            queryset, status = self.db_handler.run_sql(sql, values=[video_path])
        except Exception as e:
            print('Unable to get titles ' + str(e))
            status = False
        finally:
            return queryset, status

    def set_titles(self, old_titles_list, new_titles_list, video_path):
        queryset = None
        status = True

        try:
            for title in new_titles_list:
                if title in old_titles_list:
                    old_titles_list.remove(title)
                else:
                    sql = """ INSERT INTO video_title (video_path, title) VALUES (?, ?)"""
                    queryset, status = self.db_handler.run_sql(sql, values=[video_path, title])

            for title in old_titles_list:
                sql = """ DELETE FROM video_title WHERE video_path=? AND title=?"""
                queryset, status = self.db_handler.run_sql(sql, values=[video_path, title])
        except Exception as e:
            print('Unable to set titles ' + str(e))
            status = False

        finally:
            return queryset, status
