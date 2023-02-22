from .DBConfig import CONFIG


class settingClass():
	

	def __init__(self, registry):
		self.registry = registry
		self.load_setting()
		
	def load_setting(self):
		queryset, status = self.registry.db_handler.get_setting()
		self.db_path = CONFIG['db_path']
		self.cover_img_path = (queryset[0]['img_path'])
		self.cover_pic_format = (queryset[0]['cover_pic_format'])
		self.tag_number = (queryset[0]['tag_number'])
		self.show_browser = (bool(queryset[0]['show_browser']))		
		self.wait_min = (queryset[0]['wait_min'])
		self.wait_max = (queryset[0]['wait_max'])
		self.multi_instance = (bool(queryset[0]['multi_instance']))	


