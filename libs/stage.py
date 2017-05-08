import libs
import util.func as func
import generalEquations as equ
import libs.query as q


class Stage:

	def __init__(self, stage_specs):
		self.fuel_used = 0.0
		self.fueling_engines = []
		self.holding_engines = []
		for key, value in stage_specs.iteritems():
			setattr(self, key, value)

	def get_fuel_used(self):
		return self.fuel_used

	def get_fuel_remaining(self):
		fuel_remaining = self.fuel - self.fuel_used
		assert not self.attached or fuel_remaining > 0
		return fuel_remaining

	def get_fuel_burn_rate(self):
		burn = 0.0
		for engine in self.fueling_engines:
			burn += engine.get_eff_fuel_burn_rate()
		return burn

	def jettison(self):
		print("\nEVENT: Jettisoned {}".format(self.name))
		self.attached = False
		# if rocket total weight is calculated on total values change to be fueled_weight:
		# if rocket total weight is calculated on lift-off values use this:
		self.fuel_used = self.lift_off_weight
