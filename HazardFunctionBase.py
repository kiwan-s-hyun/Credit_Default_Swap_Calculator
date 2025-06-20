class HazardFunction:
    def __init__(self):
        pass

    def hazard_rate(self, *args, **kwargs):
        pass

    def pdf(self, time, *args, **kwargs):
        pass

    def cdf(self, start_time, end_time, survival: bool=True, *args, **kwargs):
        pass

    def discounted_cdf(self, start_time, end_time, *args, **kwargs):
        pass