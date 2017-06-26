''' create a json spec file regarding the specs of a heavy lift vehicle '''
from functools import partial
import util.func as func
from libs.vehicleFactory import VehicleFactory
from libs.query import Query as q
import libs.fileManager as fileMan


class Spec_manager(object):
	''' manages the creator and editing of spec files '''
	@classmethod
	def get_spec_functions(cls, specs):
		return {
				"Name and MK": {
					"keys" : ["name", "MK"],
					"update_function" : cls.query_name_and_MK,
					},
				"lift_off_weight": cls.query_lift_off_weight,
				"stages": cls.create_stages_specs,
				"engines": lambda: cls.change_engines(specs),
				"earth_rotation_mph": cls.query_earths_rotation
		}

	@staticmethod
	def create_stage_specs(stage_type, fuel_type):
		''' query for stage specs '''
		print(f"\n     {stage_type}\n")
		stage_specs = {}
		stage_specs['attached'] = True
		stage_specs['adc_K'] = q.query_float("What is the ADC K of the {}? ". format(stage_type))
		stage_specs['initial_weight'] = q.query_float("What is the total weight of the {}? ".format(stage_type))
		stage_specs['preburned'] = q.query_float("Weight of fuel burned by {} only, prior to lift-off? ".format(stage_type))
		stage_specs['lift_off_weight'] = stage_specs['initial_weight'] - stage_specs['preburned']

		print("The lift off weight is {}".format(stage_specs['lift_off_weight']))

		if stage_type != "orbiter":
			stage_specs['jettison_weight'] = q.query_float("What is the jettison weight of the {}? ".format(stage_type))
			if stage_type != "SRB":
				stage_specs['jettison_time'] = q.query_float("What is the jettison time of the {}? ".format(stage_type))
			else:
				stage_specs['jettison_time'] = None
		else:
			stage_specs['jettison_weight'] = 0
			stage_specs['jettison_time'] = None
		stage_specs['fuel'] = stage_specs['lift_off_weight'] - stage_specs['jettison_weight']
		stage_specs['name'] = stage_type
		stage_specs['fuel_type'] = fuel_type
		print("Fuel to be burned in {} is {}".format(stage_type, stage_specs['fuel']))
		return stage_specs


	@classmethod
	def create_stages_specs(cls):
		''' queries for stage specs '''
		stages = {}
		stage_types = ["RLV", "orbiter"]
		attach_SRB = q.query_yes_no("Does the rocket have a SRB? ", "yes")
		if attach_SRB:
			stage_types = ["SRB"] + stage_types
		attach_LFB = q.query_yes_no("Does the rocket have a LFB? ", "no")
		if attach_LFB:
			stage_types = ["LFB"] + stage_types

		for stage_type in stage_types:
			if stage_type == "SRB":
				fuel_type = "Solid"
			else:
				fuel_type = "Liquid"
			stages[stage_type] = cls.create_stage_specs(stage_type, fuel_type)
		return stages

	query_vehicle_name = staticmethod(partial(q.query_string, "What is the vehicle called (for example: HLV * 4-8/6-9)? "))
	query_vehicle_MK = staticmethod(partial(q.query_string, "MK? ", "1"))
	query_lift_off_weight = staticmethod(partial(q.query_float, "What is the HLV Gross Lift-Off Weight in Lbm? "))
	query_earths_rotation = staticmethod(partial(
										q.query_float,
										"earth rotation mph (hit enter for the default value of 912.67)? ",
										912.67
									))

	@classmethod
	def query_name_and_MK(cls):
		''' query for the name and MK to create the name, MK, friendly_name and file_name keys '''
		name = cls.query_vehicle_name()
		MK = cls.query_vehicle_MK()
		friendly_name = "{} MK {}".format(name, MK)
		clean_name = func.remove_non_alphanumeric(name)
		clean_MK = func.remove_non_alphanumeric(MK)
		file_name = "{}_MK_{}".format(clean_name, clean_MK)

		name_spec = {
			"name" : name,
			"MK" : MK,
			"friendly_name" : friendly_name,
			"file_name" : "save/specs/"+file_name
		}

		name_spec.update(VehicleFactory.collect_version())
		name_spec['friendly_name'] += " " + name_spec['version_name']
		return name_spec

	@classmethod
	def create_specs(cls):
		''' query for the specs for a heavy lift vehicle '''

		specs = {}

		keys = [
			"Name and MK",
			"lift_off_weight",
			"stages",
			"earth_rotation_mph"
		]

		for key in keys:
			specs.update(cls.change_spec(specs, key))

		selected_engines = []
		for stage_name, stage_data in specs["stages"].items():
			print('\n     ' + stage_name + '\n')
			selected_engines += VehicleFactory.select_engines(stage_name, stage_data["jettison_time"], stage_data["fuel_type"])

			specs.update({
				"engines" : selected_engines,
			})


		specs.update(VehicleFactory.collect_launch_pad())
		specs.update(VehicleFactory.collect_goals())

		fileMan.ask_to_save(specs, "Do you want to save these specs? ")

		return specs

	@staticmethod
	def change_engines(specs):
		''' Add or remove engines from a specs file and returns the engine specs (not the whole spec file) '''
		chosen_stage = q.query_from_list("option", "Choose a stage:", [stage for stage in specs["stages"]], False)
		if "engines" in specs:
			chosen = q.query_from_list("option", "Add or remove?", ["Add", "Remove"], False)
		else:
			chosen = "Add"
		if (chosen == "Add"):
			selected_engines = []
			selected_engines += VehicleFactory.select_engines(chosen_stage, specs["stages"][chosen_stage]["fuel_type"])
			try:
				specs["engines"] += selected_engines
			except KeyError:
				# if this is the first engine, you can't add to the list:
				specs["engines"] = selected_engines
		if (chosen == "Remove"):
			selected_engine = q.query_from_list(
				"option",
				"Choose an engine to remove?",
				[engine["engine_name"] for engine in specs["engines"] if engine["stage"] == chosen_stage],
				False
			)
			for i, engine in enumerate(specs["engines"]):
				if engine["engine_name"] == selected_engine:
					del specs["engines"][i]
		return specs["engines"]

	@classmethod
	def change_specs(cls, specs):
		''' chages the specs of a rocket
			More generally, modify a dict using a dict of callbacks
		'''

		spec_functions = cls.get_spec_functions(specs)
		change_another_property = True
		while (change_another_property):
			chosen_key = q.query_from_list("option", "Choose a property to change:", spec_functions.keys(), False)
			cls.change_spec(specs, chosen_key)
			change_another_property = q.query_yes_no("Change another property?")

		fileMan.ask_to_save(specs, "Do you want to save these changes? ")


	@classmethod
	def print_spec_value(cls, specs, key):
		''' prints the spec value if it exists '''
		spec_functions = cls.get_spec_functions(specs)
		# Try printing the current value if it exists
		try:
			if isinstance(specs[key], str):
				print("The current value is {}".format(specs[key]))
			else:
				print("The current value is: ")
				func.pretty_json(specs[key])

		except KeyError:
			try:
				keys = spec_functions[key]["keys"]
				if keys[0] in specs:
					print("The current values are: ")
				for key in keys:
					print("{}: {}".format(key, specs[key]))
			except KeyError:
				pass
			except TypeError:
				pass

	@classmethod
	def change_spec(cls, specs, key):
		''' change a spec using the matching spec function callback '''
		prior_specs = specs
		spec_functions = cls.get_spec_functions(specs)

		cls.print_spec_value(specs, key)
		try:
			# use the update function if the key's value is a dict rather than a callback
			specs.update(spec_functions[key]["update_function"]())
		except TypeError:
			specs[key] = spec_functions[key]()

		cls.print_spec_value(specs, key)
		edit_again = q.query_yes_no("Discard changes and edit this field again?", "no")
		if edit_again:
			return cls.change_spec(prior_specs, key)
		else:
			return specs




	@classmethod
	def get_specs(cls):
		''' get specs by asking the user to create them or select an existing file from a list '''
		return fileMan.get_json_file_data("save/specs", "spec", cls.create_specs)
