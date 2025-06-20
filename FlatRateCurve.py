import numpy as np
from DiscountCurveBase import DiscountCurve

class FlatRate(DiscountCurve):
    def __init__(self, rfr: float):
        super().__init__()
        self.rfr = rfr

    def update_rate(self, new_rfr: float):
        self.rfr = new_rfr

    def get_discount_rate(self, start_time, end_time):
        return self.rfr

    def get_discount_rate_series(self, start_time, end_time):
        return {0: (self.get_discount_rate(start_time=start_time, 
                                           end_time=end_time), 
                    start_time, end_time)}

    def get_discount_factor(self, start_time, end_time):
        rate = self.get_discount_rate(
            start_time=start_time,
            end_time=end_time
        )
        delta_t = end_time - start_time
        return np.exp(-rate * delta_t)

    def get_discount_factor_series(self, start_time, end_time):
        return {0: (self.get_discount_factor(start_time=start_time,
                                             end_time=end_time), 
                    start_time, end_time)}