
class user():
	def __init__(self) -> None:
		self.username = None
	
	def add_class(self):
		return False

	def view_class(self):
		return False

	def add_tag(self):
		return False

	def view_tag(self):
		return False

	def add_desc(self):
		return False

	def view_desc(self):
		return False

	def edit_setting(self):
		return False

	def edit_users(self):
		return False
		
	def edit_profile(self):
		return False
		
	def view_profiles(self):
		return False

	def edit_sequence(self):
		return False
		
	def get_report(self):
		return False
		
	def edit_special_video(self):
		return False

	def view_special_video(self):
		return False

class guest(user):
	def __init__(self) -> None:
		super().__init__()
		self.user_access_string = ['guest']


	def view_class(self):
		return True

	def view_tag(self):
		return True

	def view_desc(self):
		return True

	def view_special_video(self):
		return True

class admin(guest):
	def __init__(self) -> None:
		super().__init__()
		self.user_access_string += ['admin']

	def add_class(self):
		return True

	def add_tag(self):
		return True

	def add_desc(self):
		return True
	
	def view_profiles(self):
		return True
		
	def edit_profile(self):
		return True

	def edit_sequence(self):
		return True
		
	def get_report(self):
		return True
		
	def edit_special_video(self):
		return True

class mainAdmin(admin):
	def __init__(self) -> None:
		super().__init__()
		self.user_access_string += ['main_admin']

	def edit_setting(self):
		return True
	
	def edit_users(self):
		return True

class superuser(mainAdmin):
	def __init__(self) -> None:
		super().__init__()
		self.user_access_string += ['superuser']

	
	