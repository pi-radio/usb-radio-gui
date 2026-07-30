class Interval:
    def __init__(self, start, end):
        if start > end:
            start, end = end, start
        self.start = start
        self.end = end

    @property
    def center(self):
        return (self.start + self.end) / 2

    @property
    def width(self):
        return self.end - self.start
        
    def __contains__(self, v):
        if isinstance(v, Interval):
            return (v.start >= self.start) and (v.end <= self.end)
        
        return self.start <= v <= self.end

    def __hash__(self):
        return hash(self.start) ^ hash(self.end)

    def __add__(self, other):
        assert not isinstance(other, Interval)
        
        return Interval(self.start + other, self.end + other)

    def __radd__(self, other):
        return self + other


    def __sub__(self, other):
        assert not isinstance(other, Interval)
        
        return Interval(self.start - other, self.end - other)

    def __rsub__(self, other):
        return -self + other

    def __neg__(self):
        return Interval(-self.end, -self.start)
