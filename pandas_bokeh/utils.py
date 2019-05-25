from bokeh.models import (
    FuncTickFormatter,
    NumeralTickFormatter,
    BasicTickFormatter,
    PrintfTickFormatter,
    CategoricalTickFormatter,
    DatetimeTickFormatter,
    MercatorTickFormatter,
    LogTickFormatter
)


def get_tick_formatter(formatter_arg):

    if isinstance(formatter_arg, (
            FuncTickFormatter,
            NumeralTickFormatter,
            BasicTickFormatter,
            PrintfTickFormatter,
            CategoricalTickFormatter,
            DatetimeTickFormatter,
            MercatorTickFormatter,
            LogTickFormatter)):
        print("returning custom formatter")
        return formatter_arg
    if isinstance(formatter_arg, str):
        print(NumeralTickFormatter(format=formatter_arg))
        return NumeralTickFormatter(format=formatter_arg)