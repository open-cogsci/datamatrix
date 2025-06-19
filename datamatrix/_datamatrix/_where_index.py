class WhereIndex(list):
    """Primarily serves as a list-like object that is returned with where-like
    operations:
    
        where_index = dm[dm.col == 1]

    However, for compariblity with dataframe, this list-like object should also
    be able to provide access to columns, like so:
    
        dm[dm.col == 1]['col'] = 2
    """    
    def __init__(self, dm, values):
        self._dm = dm
        super().__init__(values)
    
    def __getitem__(self, key):
        if not isinstance(key, int):
            return self._dm[key]
        return key
