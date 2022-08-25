import streamlit as st
import pandas as pd
from modules.data_query import DataQuery
from modules.utils import run_concurrent_queries, estimate_gigabytes_scanned
from modules.sql_queries import (
    QUERY_POLLUTION,
    QUERY_TEMPERATURE,
    QUERY_PRCP,
    NAMES_TO_CODES,
    STATES,
    YEARS,
)
from google.cloud import bigquery
from modules.plot import plot_pol, plot_temp, plot_prc
import urllib

# Define BigQuery client
CLIENT = bigquery.Client()


def main():
    # Render the readme as markdown using st.markdown.
    readme_text = st.markdown(get_file_content_as_string("instructions.md"))

    # Add a selector for the app mode on the sidebar.
    st.sidebar.title("Navigation")

    app_mode = st.sidebar.radio(
        "Choose the app mode", ["Show instructions", "Run the app"]
    )

    if app_mode == "Show instructions":
        st.sidebar.success('To continue select "Run the app".')
    elif app_mode == "Run the app":
        readme_text.empty()
        run_the_app()


# This is the main app which appears when the user selects "Run the app".
def run_the_app():
    # To make Streamlit fast, st.cache allows us to reuse computation across runs.
    # Here we load latitude/longitude only once
    @st.cache
    def load_lat_log(file):
        return pd.read_csv(file, sep=";")

    # In the sidebar, the user select a state and a year and hit run
    state_name, year = frame_selector_ui()

    # Draw an altair chart for the map
    # xy_states = load_lat_log("data/xy_states.csv")
    # Map plot are not updated, problem from streamlit
    # data = xy_states[xy_states.state == state_name[0]][['latitude', 'longitude']]
    # st.write(data)

    # ATTENTION: NOT WORKING PROPERLY
    # Github issue: https://github.com/streamlit/streamlit/issues/475
    # For now, showing the map of the US only

    st.deck_gl_chart(
        viewport={"latitude": 42.0682, "longitude": -96.7420, "zoom": 3, "pitch": 40}
    )

    st.markdown("Made with ♡ by [Imad](https://imadelhanafi.com)")


@st.cache(allow_output_mutation=True)
def get_data(state, year):
    # Define queries
    queries_map = {
        "temperature": [QUERY_TEMPERATURE, NAMES_TO_CODES[state]],
        "pollution": [QUERY_POLLUTION, state],
        "precipitations": [QUERY_PRCP, NAMES_TO_CODES[state]],
    }

    queries_fetchers = [
        DataQuery(name, queries_map[name][0], queries_map[name][1], year)
        for name in queries_map
    ]

    results = run_concurrent_queries(queries_fetchers)

    return results


def compute_size_query(state, year):
    queries_map = {
        "temperature": [QUERY_TEMPERATURE, NAMES_TO_CODES[state]],
        "pollution": [QUERY_POLLUTION, state],
        "precipitations": [QUERY_PRCP, NAMES_TO_CODES[state]],
    }

    queries_fetchers = [
        DataQuery(name, queries_map[name][0], queries_map[name][1], year)
        for name in queries_map
    ]

    return sum(estimate_gigabytes_scanned(q.query, CLIENT) for q in queries_fetchers)


# This sidebar UI
def frame_selector_ui():
    st.sidebar.markdown("# State")

    # The user can pick a state and a year
    state_name = st.sidebar.selectbox("Select a state", STATES, 4)

    st.sidebar.markdown("# Year")

    year = st.sidebar.selectbox("Select the year of statistics", YEARS, 20)

    # Manual running
    # SQL queries are heavy, we will run only if the user hit Run
    if st.sidebar.button(" Run "):
        # Call function to run the queries and return data
        weights_warning = st.warning("Quering data from Big Query...")
        results = get_data(state_name[1], year)
        weights_warning.empty()

        # Plot1
        fig = plot_pol(results["pollution"])
        st.altair_chart(fig, width=-1)

        # Plot2
        fig = plot_temp(results["temperature"])
        st.plotly_chart(fig)

        # Plot3
        fig = plot_prc(results["precipitations"])
        st.plotly_chart(fig)

    else:
        # call function to Compute how much data will be processed
        weights_warning = st.warning("Computing query size...")
        size = compute_size_query(state_name[1], year)
        weights_warning.empty()
        st.success(
            "The query for the selected state and year will process %6.2f GB of data on BigQuery. \t Click run to get the results."
            % size
        )

    return state_name, year


@st.cache(show_spinner=False)
def get_file_content_as_string(path):
    with open(path, "r") as myfile:
        return myfile.read()


if __name__ == "__main__":
    main()
