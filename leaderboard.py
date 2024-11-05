import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import json  # Import the json module
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# Loading Data


# time to live - you can change this as it is required to be refereshed
@st.cache_data(ttl=5)
def load_data(sheet_url):
    try:
        data = pd.read_csv(sheet_url)
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Function to create a bar chart based on the specified metric

def create_bar_chart_seperate(df, entity, metric, title):
    filtered_df = df[df['Entity'] == entity]
    fig = px.bar(filtered_df, x='Function', y=metric, title=title, labels={
                 'Function': 'Function', 'Entity': 'Entity', metric: metric}, color='Function')
    return fig

# Function to create a bar chart based on the total points of each entity

def create_bar_chart(entity_sum):
    # Convert entity sum dictionary to DataFrame
    df_entity_sum = pd.DataFrame.from_dict(entity_sum, orient='index')

    # Reset index to make entity a column instead of index
    df_entity_sum.reset_index(inplace=True)
    df_entity_sum.rename(columns={'index': 'Entity'}, inplace=True)

    # Create a bar chart using Plotly Express
    fig = px.bar(df_entity_sum, x='Entity', y='Total', title='Total Score', labels={
                 'Entity': 'Entity', 'Total': 'Total Points'}, color='Entity')

    # Hide the legend
    fig.update_layout(showlegend=False)

    return fig

# Function to calculate the total 'Applied' related to each entity

def calculate_total_applied(df):
    entity_applied_total = {}
    for index, row in df.iterrows():
        entity = row['Entity']
        applied = row['Applied']
        if entity not in entity_applied_total:
            entity_applied_total[entity] = applied
        else:
            entity_applied_total[entity] += applied
    return entity_applied_total

# Function to calculate the total 'Approved' related to each entity

def calculate_total_approved(df):
    entity_approved_total = {}
    for index, row in df.iterrows():
        entity = row['Entity']
        approved = row['Approved']
        if entity not in entity_approved_total:
            entity_approved_total[entity] = approved
        else:
            entity_approved_total[entity] += approved
    return entity_approved_total

# Function to calculate the total points of each entity

def calulate_total_points(df):
    entity_sum = {}
    for index, row in df.iterrows():
        entity = row['Entity']
        total = row['Total']
        if entity not in entity_sum:
            entity_sum[entity] = total
        else:
            entity_sum[entity] += total
    return entity_sum

# Function to calculate the count of 'Applied' related to each entity based on the selected function

def count_applied_by_entity(df, selected_function):
    filtered_df = df[df['Function'] == selected_function]
    applied_counts = filtered_df.groupby(
        'Entity')['Applied'].sum().reset_index()
    applied_counts.rename(columns={'Applied': 'Count_Applied'}, inplace=True)
    return applied_counts

# Function to calculate the count of 'Approved' related to each entity based on the selected function

def count_approved_by_entity(df, selected_function):
    filtered_df = df[df['Function'] == selected_function]
    approved_counts = filtered_df.groupby(
        'Entity')['Approved'].sum().reset_index()
    approved_counts.rename(
        columns={'Approved': 'Count_Approved'}, inplace=True)
    return approved_counts

icon_path = 'https://lh3.googleusercontent.com/d/19CS85s1g6wqAdHJ-JBL_nEoaE1rzgK9C'

def calculate_approval_ranks(df):
    # Sort the DataFrame by 'Total_Approved' column in descending order
    df_sorted = df.sort_values(by='Total_Approved', ascending=False)
    # Add a new column 'Rank' to store the ranks
    df_sorted['Rank'] = range(1, len(df_sorted) + 1)

    return df_sorted


def calculate_ranks_on_score(df):
    # Sort the DataFrame by 'Total' column in descending order
    df_sorted = df.sort_values(by='Total', ascending=False)
    # Add a new column 'Rank' to store the ranks
    df_sorted['Rank'] = range(1, len(df_sorted) + 1)

    return df_sorted


#def display_approval_ranks(df):
    # Calculate ranks based on approvals
    df_with_ranks = calculate_approval_ranks(df)

    # Drop the index column
    df_without_index = df_with_ranks[['Rank', 'Entity', 'Total_Approved']]
    # Rename the column 'Total_Approved' to 'Total Approvals'
    df_with_ranks.rename(
        columns={'Total_Approved': 'Total Approvals'}, inplace=True)

    # Apply gold, silver, and bronze medals to the 'Entity' column
    df_with_ranks['Entity'] = df_with_ranks.apply(lambda row:
                                                  f"🥇 {row['Entity']}" if row['Rank'] == 1 else
                                                  f"🥈 {row['Entity']}" if row['Rank'] == 2 else
                                                  f"🥉 {row['Entity']}" if row['Rank'] == 3 else
                                                  row['Entity'], axis=1)

    # Calculate the total of the 'Total Approvals' column
    tot_ap_approvals = df_with_ranks['Total Approvals'].sum()

    # display the leaderboard section
    display_leaderboard_table(df_with_ranks, tot_ap_approvals)


def display_score_ranks(df):
    # Calculate ranks based on scores
    df_with_ranks = calculate_ranks_on_score(df)

    # Replace rank number with - if the total is 0
    df_with_ranks['Rank'] = df_with_ranks.apply(lambda row:
                                                '-' if row['Total'] == 0 else row['Rank'], axis=1)

    # Apply gold, silver, and bronze medals to the 'Entity' column
    df_with_ranks['Entity'] = df_with_ranks.apply(lambda row:
                                                  f"🥇 {row['Entity']}" if (row['Rank'] == 1 and row['Total'] !=0) else
                                                  f"🥈 {row['Entity']}" if (row['Rank'] == 2 and row['Total'] !=0) else
                                                  f"🥉 {row['Entity']}" if (row['Rank'] == 3 and row['Total'] !=0) else
                                                  row['Entity'], axis=1)

    # display the leaderboard section
    return df_with_ranks


def applied_bar_chart_and_data(data):
    # Calculate total 'Applied' related to each entity
    entity_applied_total = calculate_total_applied(data)

    # Convert dictionary to DataFrame
    df_entity_applied_total = pd.DataFrame.from_dict(
        entity_applied_total, orient='index', columns=['Total_Applied'])
    df_entity_applied_total.reset_index(inplace=True)
    df_entity_applied_total.rename(columns={'index': 'Entity'}, inplace=True)

    # Create a colored bar chart using Plotly Express
    fig_applied = px.bar(df_entity_applied_total, x='Entity', y='Total_Applied', title='🌍 Total Applications by Entity', labels={
                         'Entity': 'Entity', 'Total_Applied': 'Applications'}, color='Entity')

    # Hide the legend
    fig_applied.update_layout(
        title_font=dict(size=20, color="#31333F"),  # Title font size
        # X-axis title font size
        xaxis_title_font=dict(size=16, color="#31333F"),
        # Y-axis title font size
        yaxis_title_font=dict(size=16, color="#31333F"),
        xaxis_tickfont=dict(size=14, color="#31333F"),  # X-axis tick font size
        yaxis_tickfont=dict(size=14, color="#31333F"),  # Y-axis tick font size
        showlegend=False
    )

    return fig_applied, df_entity_applied_total


def approved_bar_chart_and_data(data):
    # Calculate total 'Approved' related to each entity
    entity_approved_total = calculate_total_approved(data)

    # Convert dictionary to DataFrame
    df_entity_approved_total = pd.DataFrame.from_dict(
        entity_approved_total, orient='index', columns=['Total_Approved'])
    df_entity_approved_total.reset_index(inplace=True)
    df_entity_approved_total.rename(columns={'index': 'Entity'}, inplace=True)
    # Create a colored bar chart using Plotly Express
    fig_approved = px.bar(df_entity_approved_total, x='Entity', y='Total_Approved', title='✅ Total Approvals by Entity', labels={
                          'Entity': 'Entity', 'Total_Approved': 'Approvals'}, color='Entity')
    # Hide the legend
    fig_approved.update_layout(
        title_font=dict(size=20, color="#31333F"),  # Title font size
        # X-axis title font size
        xaxis_title_font=dict(size=16, color="#31333F"),
        # Y-axis title font size
        yaxis_title_font=dict(size=16, color="#31333F"),
        xaxis_tickfont=dict(size=14, color="#31333F"),  # X-axis tick font size
        yaxis_tickfont=dict(size=14, color="#31333F"),  # Y-axis tick font size
        showlegend=False
    )

    return fig_approved, df_entity_approved_total


def total_points(data):
    entity_points_total = calulate_total_points(data)
    df_entity_points_total = pd.DataFrame.from_dict(
        entity_points_total, orient='index', columns=['Total'])
    df_entity_points_total.reset_index(inplace=True)
    df_entity_points_total.rename(columns={'index': 'Entity'}, inplace=True)

    # return df_ranks
    return df_entity_points_total


def display_leaderboard_table(df):
    # Apply custom CSS for styling
    st.markdown(
        """
    <style>
    th, td {
        font-size: 20px !important;
        padding: 10px; /* Add padding for better spacing */
        text-align: center; /* Center-align text */
        font-weight: 900;
    }
    table {
        width: 100%; /* Full width */
        border-collapse: collapse; /* Collapse borders */
    }
    th {
        background-color: #FCFCFC; /* Light gray background for headers */
        border: 5px solid #ddd; /* Add borders to header */
    }
    td {
        border: 1px solid #ddd; /* Add borders to cells */
    }
    </style>
    """, unsafe_allow_html=True)

    # Calculate ranks based on scores
    df_with_ranks = display_score_ranks(df)

    # Rename the columns for better readability
    df_with_ranks.rename(columns={
        'Total': 'Total Points',
        'Total_Approved': 'Total Approvals',
        'Total_Applied': 'Total Applications'
    }, inplace=True)

    # Ensure the Rank column is included and set as the index
    df_with_ranks['Rank'] = range(1, len(df_with_ranks) + 1)

    # Specify the order of columns explicitly
    # Make sure that the columns listed here match your DataFrame
    columns_order = ['Rank', 'Entity', 'Total Points',
                     'Total Approvals', 'Total Applications']

    # Check if all specified columns exist in the DataFrame
    for col in columns_order:
        if col not in df_with_ranks.columns:
            st.error(f"Column '{col}' not found in DataFrame.")
            return  # Stop execution if a column is missing

    # Reorder DataFrame to include the Rank column first
    df_with_ranks = df_with_ranks[columns_order]

    # Convert DataFrame to HTML, including the rank column as a standard column
    html_table = df_with_ranks.to_html(
        classes='dataframe', index=False, escape=False)

    # Display the HTML table
    st.markdown(html_table, unsafe_allow_html=True)
# Main Streamlit app


def main():
    st.set_page_config(
        layout="wide",
        # You can change the page title here
        page_title="Transcend Hackathon - Dashboard",
        page_icon=icon_path,
    )

    # The Dashboard Title (You can change here)
    # st.title("Transcend Hackathon - Dashboard")

    col1, col2 = st.columns([1, 15])
    with col1:
        st.image(icon_path)
    with col2:
        st.title("Hackathon - Dashboard")

    st.markdown(
        "<hr style='border: 1px solid #000; width: 100%;'>",
        unsafe_allow_html=True
    )

    # Set interval to 5 minutes
    st_autorefresh(interval=1 * 60 * 1000, key="data_refresh")
    # URL to your Google Sheets data
    # Datasource url / Google Sheets CSV
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTXOP09TlmTmfTCx5x7Dwgm8s80W4z7m9plWqbZ7Lfodxox-26BoTNDq-tozEQylR7jKa3UbtIjU1I1/pub?gid=1562137798&single=true&output=csv"

    # Load data using the cached function
    data = load_data(sheet_url)

    if data is not None:

        # Check if the 'Entity' column exists in the DataFrame
        if 'Entity' in data.columns:

            # calculation of leaderboard items
            fig_applied, df_entity_applied_total = applied_bar_chart_and_data(data)
            fig_approved, df_entity_approved_total = approved_bar_chart_and_data(data)
            df_ranks = total_points(data)

            # df_combined = pd.concat(df_ranks, df_entity_applied_total, df_entity_approved_total, on='Entity')
            # df_combined = df_ranks.merge(df_entity_applied_total, on='Entity').merge(df_entity_approved_total, on='Entity')
            df_combined = df_entity_applied_total.merge(
                df_entity_approved_total, on='Entity').merge(df_ranks, on='Entity')

            # Define a layout with two columns
            col1, col2 = st.columns([1, 1])

            # Display the total approvals in the first column
            with col1:
                st.markdown(
                    "<div style='text-align: center;'>"
                    f"<h3>✅ Total Approvals</h3>"
                    f"<p style='font-size: 32px;'>{
                        df_entity_approved_total['Total_Approved'].sum()}</p>"
                    "</div>",
                    unsafe_allow_html=True,
                )

            # Display the leaderboard in the second column
            with col2:
                st.markdown(
                    "<div style='text-align: center;'>"
                    f"<h3>🌍 Total Applications</h3>"
                    f"<p style='font-size: 32px;'>{
                        df_entity_applied_total['Total_Applied'].sum()}</p>"
                    "</div>",
                    unsafe_allow_html=True,
                )

            st.subheader('🔥Leaderboard')

            # Display the leaderboard table
            display_leaderboard_table(df_combined)

            st.plotly_chart(fig_approved, use_container_width=True)
            st.plotly_chart(fig_applied, use_container_width=True)

            ###############################################################################

            st.divider()

            st.subheader('Functional Analysis')
            # Create a select box to choose the 'Function'
            selected_function = st.selectbox(
                'Select Function', data['Function'].unique())

            # Get the count of 'Applied' related to each entity based on the selected function
            applied_counts = count_applied_by_entity(data, selected_function)

            # Create a bar chart using Plotly Express
            fig_1 = px.bar(applied_counts, x='Entity', y='Count_Applied', title=f'🌍 Applications by Entity for {
                           selected_function} Function', labels={'Entity': 'Entity', 'Count_Applied': 'Applications'}, color='Entity')
            fig_1.update_layout(
                title_font=dict(size=20, color="#31333F"),  # Title font size
                # X-axis title font size
                xaxis_title_font=dict(size=16, color="#31333F"),
                # Y-axis title font size
                yaxis_title_font=dict(size=16, color="#31333F"),
                # X-axis tick font size
                xaxis_tickfont=dict(size=14, color="#31333F"),
                # Y-axis tick font size
                yaxis_tickfont=dict(size=14, color="#31333F"),
                showlegend=False)

            # Get the count of 'Approved' related to each entity based on the selected function
            approved_counts = count_approved_by_entity(data, selected_function)

            # Create a bar chart using Plotly Express
            fig_2 = px.bar(approved_counts, x='Entity', y='Count_Approved', title=f'✅ Approvals by Entity for {
                           selected_function} Function', labels={'Entity': 'Entity', 'Count_Approved': 'Approvals'}, color='Entity')
            fig_2.update_layout(
                title_font=dict(size=20, color="#31333F"),  # Title font size
                # X-axis title font size
                xaxis_title_font=dict(size=16, color="#31333F"),
                # Y-axis title font size
                yaxis_title_font=dict(size=16, color="#31333F"),
                # X-axis tick font size
                xaxis_tickfont=dict(size=14, color="#31333F"),
                # Y-axis tick font size
                yaxis_tickfont=dict(size=14, color="#31333F"),
                showlegend=False)

            st.plotly_chart(fig_2, use_container_width=True)
            st.plotly_chart(fig_1, use_container_width=True)

            st.write("<br><br>", unsafe_allow_html=True)
            # Footer - It would be great if you could give us a recognition for the team.
            st.write("<p style='text-align: center;'>Made with ❤️ by &lt;/Dev.Team&gt; of <strong>AIESEC in Sri Lanka</strong></p>", unsafe_allow_html=True)

        else:
            st.error("The 'Entity' column does not exist in the loaded data.")
    else:
        st.error("Failed to load data.")


if __name__ == "__main__":
    main()
