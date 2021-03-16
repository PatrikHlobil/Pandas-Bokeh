import numpy as np
import pandas as pd
import pytest

from pandas_bokeh.plot import _determine_data_columns


class TestDetermineDataColumns:
    @staticmethod
    def df():
        df = pd.DataFrame(
            {
                "pd_float": np.random.random(20),
                "pd_int": np.random.randint(1, 10, 20),
                "string": np.random.choice(["a", "b"], 20),
            }
        ).convert_dtypes()

        df["float"] = np.random.randint(1, 20, 20)
        df["int"] = np.random.randint(1, 20, 20)
        return df

    @pytest.mark.parametrize(
        "y,data_cols",
        [
            (
                None,
                [
                    "pd_float",
                    "pd_int",
                    "float",
                    "int",
                ],
            ),
            (
                ["pd_float", "int"],
                ["pd_float", "int"],
            ),
            (
                "pd_int",
                ["pd_int"],
            ),
        ],
    )
    def test_determine_data_columns(self, y, data_cols):
        df = self.df()
        assert _determine_data_columns(y=y, df=df) == data_cols

    @pytest.mark.parametrize("y", ("col_not_existing", "string"))
    def test_determine_data_columns__raise_exception(self, y):
        df = self.df()
        with pytest.raises(ValueError):
            _determine_data_columns(y=y, df=df)
