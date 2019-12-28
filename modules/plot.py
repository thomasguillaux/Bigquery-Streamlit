import altair as alt
import chart_studio.plotly as py
import plotly.graph_objs as go


def plot_pol(df):
    """
    df: pandas dataframe with columns ['month', 'pm10', 'co', 'pm25_frm', 'so2', 'pm25_nonfrm']
    returns Altair plot
    """

    source = df[["month", "pm10", "co", "pm25_frm", "so2", "pm25_nonfrm"]]
    source.columns = [
        "month",
        "PM10 mass (µg/m³)",
        "CO (ppm)",
        "PM2.5 frm (µg/m³)",
        "SO2 (ppb)",
        "PM2.5 nonfrm (µg/m³)",
    ]

    source = source.melt("month", var_name="category", value_name="y")

    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(
        type="single", nearest=True, on="mouseover", fields=["month"], empty="none"
    )

    # The basic line
    line = (
        alt.Chart(source)
        .mark_line(interpolate="linear")
        .encode(x="month:Q", y="y:Q", color="category:N")
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = (
        alt.Chart(source)
        .mark_point()
        .encode(x="month:Q", opacity=alt.value(0))
        .add_selection(nearest)
    )

    # Draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = line.mark_text(align="left", dx=5, dy=-5).encode(
        text=alt.condition(nearest, "y:Q", alt.value(" "))
    )

    # Draw a rule at the location of the selection
    rules = (
        alt.Chart(source)
        .mark_rule(color="gray")
        .encode(x="month:Q")
        .transform_filter(nearest)
    )

    # Put the five layers into a chart and bind the data
    res = alt.layer(line, selectors, points, rules, text).properties(
        width=600,
        height=300,
        title="Average monthly measurement of some air pollutants",
    )

    return res


def plot_temp(df):
    """
    df: pandas dataframe with columns ['year', 'month', 'day', 'avg_temp', 'min_temp', 'max_temp']
    returns: Plotly plot
    """

    df["Time"] = df["year"] + "-" + df["month"] + "-" + df["day"]
    upper_bound = go.Scatter(
        name="Max temperature",
        x=df["Time"],
        y=df["max_temp"],
        mode="lines",
        marker=dict(color="#444"),
        line=dict(width=0),
        fillcolor="rgba(68, 68, 68, 0.3)",
        fill="tonexty",
    )

    trace = go.Scatter(
        name="Avg temperature",
        x=df["Time"],
        y=df["avg_temp"],
        mode="lines",
        line=dict(color="rgb(31, 119, 180)"),
        fillcolor="rgba(68, 68, 68, 0.3)",
        fill="tonexty",
    )

    lower_bound = go.Scatter(
        name="Min temperature",
        x=df["Time"],
        y=df["min_temp"],
        marker=dict(color="#444"),
        line=dict(width=0),
        mode="lines",
    )

    # Trace order can be important
    # with continuous error bars
    data = [lower_bound, trace, upper_bound]

    layout = go.Layout(
        yaxis=dict(title="Temperature in F"),
        title="Temperature (avg, min, max) for selected year and state",
        # plot_bgcolor='#ffffff',
        showlegend=False,
    )

    fig = go.Figure(data=data, layout=layout)
    # fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='Grey')
    # fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='Grey')

    return fig


def plot_prc(df):
    """
    df: pandas dataframe with columns ['year', 'month', 'day', 'prcp']
    """
    df["Time"] = (
        df["year"].apply(str)
        + "-"
        + df["month"].apply(str)
        + "-"
        + df["day"].apply(str)
    )

    trace1 = go.Bar(x=df["Time"], y=df["prcp"], marker=dict(color="rgb(55, 83, 109)"))

    layout = go.Layout(
        title="Precipitation in mm",
        yaxis=dict(title="mm"),
        barmode="group",
        bargap=0.15,
        bargroupgap=0.1,
        # plot_bgcolor='#ffffff',
        showlegend=False,
    )

    fig = go.Figure(data=trace1, layout=layout)
    # fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='Grey')
    # fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='Grey')

    return fig
