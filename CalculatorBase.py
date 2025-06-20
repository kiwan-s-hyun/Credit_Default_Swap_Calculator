import numpy as np
from math import floor, ceil
from scipy.optimize import root_scalar
from DiscountCurveBase import DiscountCurve
from ConstantHazardRateFunction import ConstantHazardFunction

debug_output = False

class ProtectionLeg:
	def __init__(self, lambda_: float, notional: float, recovery_rate: float,
				 discount_curve: DiscountCurve):
		self.notional = notional
		self.recovery_rate = recovery_rate
		self.discount_curve = discount_curve
		self.hazard_function = ConstantHazardFunction(
			lambda_=lambda_
		)

	def update_lambda(self, new_lambda: float):
		self.hazard_function.update_lambda(
			new_lambda=new_lambda
		)

	def update_notional(self, new_notional: float):
		self.notional = new_notional

	def update_recovery_rate(self, new_recovery_rate: float):
		self.recovery_rate = new_recovery_rate

	def update_discount_curve(self, new_discount_curve: DiscountCurve):
		self.discount_curve = new_discount_curve

	def get_PV(self, start_time: float, end_time: float, 
			   valulation_time: float=None):
		coverage_amnt = self.notional * (1 - self.recovery_rate)
		if valulation_time is not None:
			accrued_discount = self.discount_curve.get_discount_factor(
				start_time=start_time,
				end_time=valulation_time
			)
		else:
			accrued_discount = 1

		discount_rate_series = self.discount_curve.get_discount_rate_series(
			start_time=start_time,
			end_time=end_time
		)
		discounted_EPD = self.hazard_function.discounted_cdf(
			discount_rate_series=discount_rate_series
		)

		return coverage_amnt * discounted_EPD / accrued_discount

class PremiumLeg:
	def __init__(self, lambda_: float, notional: float, cpn: float, 
			     cpn_freq: float, discount_curve: DiscountCurve, 
				 accrual_adjustment: bool=True):
		self.notional = notional
		self.cpn = cpn
		self.cpn_freq = cpn_freq
		self.discount_curve = discount_curve
		self.hazard_function = ConstantHazardFunction(
			lambda_=lambda_
		)
		self.accrual_adjustment = accrual_adjustment

	def update_lambda(self, new_lambda: float):
		self.hazard_function.update_lambda(
			new_lambda=new_lambda
		)

	def update_notional(self, new_notional: float):
		self.notional = new_notional

	def update_cpn(self, new_cpn: float):
		self.cpn = new_cpn

	def update_cpn_freq(self, new_cpn_freq: float):
		self.cpn = new_cpn_freq

	def update_discount_curve(self, new_discount_curve: DiscountCurve):
		self.discount_curve = new_discount_curve

	def get_PV(self, start_time, end_time, valulation_time: float=None):
		if valulation_time is not None:
			accrued_discount = self.discount_curve.get_discount_factor(
				start_time=start_time,
				end_time=valulation_time
			)
		else:
			accrued_discount = 1
		annl_cpn = self.notional * self.cpn
		std_cpn_pymnt = annl_cpn / self.cpn_freq
		max_accrual_period = ceil(end_time * self.cpn_freq)
		min_accrual_period = floor(start_time * self.cpn_freq)
		accrual_periods = [_ / self.cpn_freq for _ in 
					       range(min_accrual_period, max_accrual_period + 1)]
		PV = 0
		total_discount = np.prod(
			[_[0] for _ in self.discount_curve.get_discount_factor_series(
				start_time=start_time,
				end_time=accrual_periods[0]
			).values()]
		)
		for accrual_start, accrual_end in zip(accrual_periods[:-1],
										      accrual_periods[1:]):
			discount_series = self.discount_curve.get_discount_factor_series(
				start_time=accrual_start,
				end_time=accrual_end
			)
			total_discount *= np.prod([_[0] for _ in discount_series.values()])
			survival_prob = self.hazard_function.cdf(
				start_time=start_time,
				end_time=accrual_end,
				survival=True
			)
			base_adj = total_discount * survival_prob
			cpn_PV = std_cpn_pymnt * base_adj

			if self.accrual_adjustment:
				discounted_EPD = self.hazard_function.discounted_accrual_cdf(
						discount_rate_series=discount_series
				)
				accrued_PV = annl_cpn * base_adj * discounted_EPD
			else:
				accrued_PV = 0
			PV += cpn_PV + accrued_PV
		
		return PV / accrued_discount

class SpreadCalculator:
	def __init__(self, discount_curve: DiscountCurve, tenor: float, 
			     notional: float, recovery_rate: float, cpn: float, 
				 cpn_freq: float, cds_rel_start: float=0.0, 
				 valulation_time: float=None):
		self.discount_curve = discount_curve
		self.tenor = tenor
		self.notional = notional
		self.recovery_rate = recovery_rate
		self.cpn = cpn
		self.cpn_freq = cpn_freq
		self.protection_leg = ProtectionLeg(
			lambda_=0.0,
			notional=notional,
			recovery_rate=recovery_rate,
			discount_curve=discount_curve
		)
		self.premium_leg = PremiumLeg(
			lambda_=0.0,
			notional=notional,
			cpn=cpn,
			cpn_freq=cpn_freq,
			discount_curve=discount_curve
		)
		self.cds_rel_start = cds_rel_start
		self.valuation_time = valulation_time

	def update_notional(self, new_notional: float):
		self.notional = new_notional
		self.protection_leg.update_notional(
			new_notional=new_notional
		)
		self.premium_leg.update_notional(
			new_notional=new_notional
		)

	def update_discount_curve(self, new_discount_curve: DiscountCurve):
		self.discount_curve = new_discount_curve
		self.protection_leg.update_discount_curve(
			new_discount_curve=new_discount_curve
		)
		self.premium_leg.update_discount_curve(
			new_discount_curve=new_discount_curve
		)

	def update_recovery_rate(self, new_recovery_rate: float):
		self.recovery_rate = new_recovery_rate
		self.protection_leg.update_recovery_rate(
			new_recovery_rate=new_recovery_rate
		)

	def update_coupon(self, new_cpn: float):
		self.cpn = new_cpn
		self.premium_leg.update_cpn(
			new_cpn=new_cpn
		)

	def update_coupon_frequency(self, new_cpn_freq: float):
		self.cpn_freq = new_cpn_freq
		self.premium_leg.update_cpn_freq(
			new_cpn_freq=new_cpn_freq
		)

	def update_cds_relative_start_time(self, new_start_time: float):
		self.cds_rel_start = new_start_time

	def update_valuation_time(self, new_valuation_time: float):
		self.valuation_time = new_valuation_time

	def evaluate_upfront(self, lambda_: float):
		self.protection_leg.update_lambda(
			new_lambda=lambda_
		)
		self.premium_leg.update_lambda(
			new_lambda=lambda_
		)

		protection_pv = self.protection_leg.get_PV(
			start_time=self.cds_rel_start, 
			end_time=self.tenor,
			valulation_time=self.valuation_time
		)

		premium_pv = self.premium_leg.get_PV(
			start_time=self.cds_rel_start, 
			end_time=self.tenor,
			valulation_time=self.valuation_time
		)

		U = protection_pv - premium_pv

		if debug_output:
				print(f'Hazard: {lambda_} --> Protection PV: {protection_pv}',
					  f', Premium PV: {premium_pv}, Upfront: {U}')

		return U

	def calculate_hazard(self, price: float, min_guess: float=1e-5, 
					     max_guess: float=1):
		f = lambda lambda_: self.evaluate_upfront(lambda_) - price
		
		results = root_scalar(f, method='brentq', 
						      bracket=[min_guess, max_guess])

		if not results['converged']:
			print(results)
			raise ValueError('Brentq Not Converged')

		lambda_star = results['root']

		if debug_output:
			print(f'Upfront: {price} --> Hazard: {lambda_star}')

		return lambda_star

	def calculate_par_spread(self, lambda_: float, return_in_bps: bool=True):
		self.protection_leg.update_lambda(
			new_lambda=lambda_
		)
		self.premium_leg.update_lambda(
			new_lambda=lambda_
		)

		par_spread_multiplier = self.protection_leg.get_PV(
			start_time=self.cds_rel_start, 
			end_time=self.tenor,
			valulation_time=self.valuation_time
		) / self.premium_leg.get_PV(
			start_time=self.cds_rel_start, 
			end_time=self.tenor,
			valulation_time=self.valuation_time
		)

		par_spread = self.cpn * par_spread_multiplier

		if debug_output:
				print(f'Hazard: {lambda_} --> Par Spread (bps):',
		              f'{par_spread * 1e4}')

		if return_in_bps:
			return par_spread * 1e4
		else:
			return par_spread

	def price_to_par_spread(self, price: float, min_guess: float=1e-5, 
						    max_guess: float=1, return_in_bps: bool=True):
		lambda_star = self.calculate_hazard(
			price=price,
			min_guess=min_guess,
			max_guess=max_guess
		)

		par_spread = self.calculate_par_spread(
			lambda_=lambda_star,
			return_in_bps=return_in_bps
		)

		return par_spread


if __name__ == '__main__':
	from FlatRateCurve import FlatRate
	discount_curve = FlatRate(rfr=0.03)
	test = SpreadCalculator(
		discount_curve=discount_curve,
		tenor=5,
		notional=100,
		recovery_rate=0.4,
		cpn=0.01,
		cpn_freq=4
	)

	par_spread = test.price_to_par_spread(
		price=2.55,
		return_in_bps=True
	)

	print(par_spread)