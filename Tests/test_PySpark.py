import os
import sys

import numpy as np
import pandas as pd
import pytest

import pandas_bokeh

BASE_DIR = os.path.dirname(__file__)
os.makedirs(os.path.join(BASE_DIR, "Plots"), exist_ok=True)


@pytest.fixture
def spark():
    # Start PySpark
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()
    yield spark
    spark.stop()


@pytest.mark.skipif(
    sys.version_info >= (3, 10), reason="Pyspark 3.2.1 requires Python <= 3.9"
)
def test_basic_lineplot_pyspark(spark):
    """Test for basic lineplot with Pyspark"""

    # Create basic lineplot:
    np.random.seed(42)
    df = pd.DataFrame(
        {
            "Google": np.random.randn(1000) + 0.2,
            "Apple": np.random.randn(1000) + 0.17,
        },
        index=pd.date_range("1/1/2000", periods=1000),
    )
    df.index.name = "Date"
    df = df.cumsum()
    df = df + 50
    df = spark.createDataFrame(df.reset_index())
    p_basic_lineplot = df.plot_bokeh(kind="line", x="Date", show_figure=False)
    p_basic_lineplot_accessor = df.plot_bokeh.line(x="Date", show_figure=False)

    # Output plot as HTML:
    output = pandas_bokeh.row([p_basic_lineplot, p_basic_lineplot_accessor])
    with open(os.path.join(BASE_DIR, "Plots", "Basic_lineplot_PySpark.html"), "w") as f:
        f.write(pandas_bokeh.embedded_html(output))

    assert True
