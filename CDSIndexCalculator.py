from DiscountCurveBase import DiscountCurve
from CalculatorBase import SpreadCalculator

class CDXIGCalculator(SpreadCalculator):
    def __init__(self, discount_curve: DiscountCurve, tenor: float, 
                 series_rel_start: float=0.0, valulation_time: float=None):
        super().__init__(
            discount_curve=discount_curve,
            tenor=tenor,
            notional=100,
            recovery_rate=0.40,
            cpn=0.01,
            cpn_freq=4,
            cds_rel_start=series_rel_start,
            valulation_time=valulation_time
        )


class CDXHYCalculator(SpreadCalculator):
    def __init__(self, discount_curve: DiscountCurve, tenor: float, 
                 series_rel_start: float=0.0, valulation_time: float=None):
        super().__init__(
            discount_curve=discount_curve,
            tenor=tenor,
            notional=100,
            recovery_rate=0.30,
            cpn=0.05,
            cpn_freq=4,
            cds_rel_start=series_rel_start,
            valulation_time=valulation_time
        )

class ITRXEURCalculator(SpreadCalculator):
    def __init__(self, discount_curve: DiscountCurve, tenor: float, 
                 series_rel_start: float=0.0, valulation_time: float=None):
        super().__init__(
            discount_curve=discount_curve,
            tenor=tenor,
            notional=100,
            recovery_rate=0.40,
            cpn=0.01,
            cpn_freq=4,
            cds_rel_start=series_rel_start,
            valulation_time=valulation_time
        )

if __name__ == '__main__':
    from FlatRateCurve import FlatRate

    test_data = {'tenor': 5.0, 'rfr': 0.01627, 'series_rel_start': 10/365,
                 'valulation_time': None, 'price': 100 - 106.8723, 
                 'expected': 347.0937}
    
    discount_curve = FlatRate(rfr=test_data['rfr'])

    test = CDXHYCalculator(
        discount_curve=discount_curve,
        tenor=test_data['tenor'],
        series_rel_start=test_data['series_rel_start'],
        valulation_time=test_data['valulation_time']
    )

    par_spread = test.price_to_par_spread(
        price=test_data['price']    
    )

    print(f'Swap Rate: {test_data['rfr']}, ' + 
          f'Expected Output: {test_data['expected']}, ' + 
          f'Actual Output: {par_spread}')

    def f(rfr):
        test.discount_curve.update_rate(new_rfr=rfr)
        par_spread = test.price_to_par_spread(
            price=test_data['price']    
        )

        return par_spread

    import numpy as np
	
    rfrs = np.arange(1e-4, 0.2, 1e-4)
    par_spreads = np.array([f(_) for _ in rfrs])

    import matplotlib.pyplot as plt

    plt.plot(rfrs, par_spreads)
    plt.plot([rfrs[0], rfrs[-1]], 
             [test_data['expected'], test_data['expected']])
    plt.show()