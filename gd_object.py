from gd_object_dict import OBJECT_DICTIONARY


class gd_object:

	def __init__(self, **kwargs):
		self.dict = kwargs
		
	def __str__(self):
		object_string = []
		for i in self.dict:
			prop_key = str(OBJECT_DICTIONARY[i]) if i in OBJECT_DICTIONARY else str(i)
			object_string.append(prop_key)
			object_string.append(str(self.dict[i]))
		return (','.join(object_string))

	def __repr__(self):
		return self.__str__()



class gd_object_collection:

	def __init__(self, **kwargs):
		self.block_data = []

	def add_block(self, **kwargs):
		self.block_data.append(gd_object(**dict(**kwargs)))