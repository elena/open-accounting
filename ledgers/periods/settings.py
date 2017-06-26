from datetime import date


# @@ TODO this can be done better.

# Need to look up Financial Years by key.

FINANCIAL_YEARS = {
    'F15': (date(2014, 7, 1), date(2015, 6, 30)),
    'F16': (date(2015, 7, 1), date(2016, 6, 30)),
    'F17': (date(2016, 7, 1), date(2017, 6, 30)),
    'F18': (date(2017, 7, 1), date(2018, 6, 30)),
}

# Need iterable of tuples as choices.

FINANCIAL_YEARS_CHOICES = sorted([(k, k) for k, v in
                                  FINANCIAL_YEARS.items()])
