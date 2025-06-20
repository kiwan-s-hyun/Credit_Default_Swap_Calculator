import numpy as np
from HazardFunctionBase import HazardFunction

class ConstantHazardFunction(HazardFunction):
    def __init__(self, lambda_: float):
        super().__init__()
        self.lambda_ = lambda_

    def update_lambda(self, new_lambda: float):
        self.lambda_ = new_lambda

    def hazard_rate(self):
        return self.lambda_

    def pdf(self, time: float):
        return self.lambda_ * np.exp(-self.lambda_ * time)

    def cdf(self, start_time: float, end_time: float, survival: bool=True):
        Q = np.exp(-self.lambda_ * (end_time - start_time))
        return Q if survival else 1 - Q

    def discounted_cdf(self, discount_rate_series: dict):
        ret = 0
        constant = self.lambda_
        for k, v in discount_rate_series.items():
            rfr = v[0]
            start_time = v[1]
            end_time = v[2]
            integral_rslt = (
                1 - np.exp(-(rfr + self.lambda_) * (end_time - start_time))    
            ) / (rfr + self.lambda_)
            ret += constant * integral_rslt
            constant *= np.exp(
                -(rfr + self.lambda_) * (end_time - start_time)
            )
        return ret

    def discounted_accrual_cdf(self, discount_rate_series: dict):
        part_1_1 = 0
        part_1_2 = 0
        constant = self.lambda_
        first_series = True
        for k, v in discount_rate_series.items():
            rfr = v[0]
            start_time = v[1]
            if first_series:
                accrual_start = start_time
                first_series = False
            end_time = v[2]
            part_1_1_integral_rslt = (
                1 - np.exp(-(rfr + self.lambda_) * (end_time - start_time))    
            ) / ((rfr + self.lambda_) ** 2)
            part_1_1 += constant * part_1_1_integral_rslt
            part_1_2 += constant / (rfr + self.lambda_) * (
                start_time - 
                end_time * np.exp(
                    -(rfr + self.lambda_) * (end_time - start_time)
                )
            )
            constant *= np.exp(
                -(rfr + self.lambda_) * (end_time - start_time)
            )
        part_1 = part_1_1 + part_1_2
        part_2 = accrual_start * self.discounted_cdf(discount_rate_series)

        return part_1 - part_2