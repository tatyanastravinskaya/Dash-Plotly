# importing main libraries
import pandas as pd
import plotly.express as px
from dash import dcc, html, Dash, Input, Output, dash_table

# PREPARING DATA BEFORE CREATING DASHBOARD
# putting data from csv files into variables finished_lesson_test and lesson_index_test
finished_lesson_test = pd.read_csv('finished_lesson_test.csv')
lesson_index_test = pd.read_csv('lesson_index_test.csv')

# merging datasets
merged_lesson = pd.merge(lesson_index_test, finished_lesson_test, on='lesson_id')

# changing data type in column date_created
merged_lesson['date_created'] = pd.to_datetime(merged_lesson['date_created'])

# choosing only analyst
merged_lesson = merged_lesson[merged_lesson['profession_name'] == 'data-analyst']

# analogue of row_number() over (partition by user_id order by date_created) as first_lesson_dt
merged_lesson['first_lesson_dt'] = merged_lesson.sort_values('date_created')\
                                       .groupby('user_id').cumcount() + 1

# creating a new table consists of users who passed their first lesson in April 2020
users = merged_lesson[(merged_lesson['first_lesson_dt'] == 1)
                      & (merged_lesson['date_created'].dt.to_period('M') == '2020-04')]['user_id']

# merging tables merged_lesson and users
# getting all information about users who passed their first lesson in April 2020
merged_lesson_new = pd.merge(merged_lesson, users, on='user_id')

# adding a column date_creates_next includes date and time of passing the next lesson
merged_lesson_new['next_date_created'] = merged_lesson_new.sort_values(by=['date_created'], ascending=True)\
                                            .groupby(['user_id'])['date_created'].shift(-1)

# counting a difference between the next and previous date of passing the lesson (sec)
merged_lesson_new['delta_seconds'] = (merged_lesson_new['next_date_created']-merged_lesson_new['date_created']).dt.seconds

# choosing all cases where the difference between passing the lessons less or equal 5 sec
final_merged_lesson = merged_lesson_new[merged_lesson_new['delta_seconds'] <= 5].iloc[:, [9, 6, 3, 8, 0, 4]]
final_merged_lesson['delta_seconds'] = final_merged_lesson['delta_seconds'].astype(int)

# PREPARING DATA FOR CREATING DASHBOARD
# grouping data by amount of seconds and getting count of UNIQUE lessons by delta_seconds
grouped_lessons_info = final_merged_lesson.groupby(['delta_seconds'])['lesson_id'].nunique().reset_index()

# bar chart
lessons_bar_chart = px.bar(
    grouped_lessons_info,
    x='delta_seconds',
    y='lesson_id',
    labels={'delta_seconds': 'Duration, seconds', 'lesson_id': 'Count of lessons'},
    text_auto=True
)
lessons_bar_chart.update_traces(marker_color='rgb(108, 156, 166)',
                                textposition='outside')
lessons_bar_chart.update_layout(clickmode='event+select')

# count of unique selected lessons
num_unique_lessons = final_merged_lesson[['lesson_id']].drop_duplicates()

# put the column lesson_id into new table
lesson_duration_new_table = final_merged_lesson.loc[:, ['lesson_id', 'delta_seconds']].drop_duplicates()

# create table with unique lesson_id for dash
unique_lessons_table = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in lesson_duration_new_table.columns],
    data=lesson_duration_new_table.to_dict('records')
)

# App layout
app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='LESSONS WITH TOO FAST COMPLETION TIME'),
    html.Div(children="""
        Given dashboard contains the number of unique lessons 
        having too fast completion time. The chart below shows 
        amount of passed lessons distributed according 
        passing time. The chart is interactive: when you click 
        on any of the columns, a list of the corresponding lessons 
        appears on the right side of the dashboard.""",
            style={'width': '50vw', 'display': 'inline-block'}),
    html.H3(id='count_lesson'),
    dcc.Graph(
        id='graph',
        figure=lessons_bar_chart,
        style={'width': '50vw', 'float': 'left', 'display': 'inline-block'}
    ),
    html.Div(children=[
        html.H3(children='List of unique lessons'),
        unique_lessons_table
    ],
        id='table',
        style={'width': '40%', 'height': '50%', 'float': 'centre', 'overflowY': 'scroll', 'display': 'inline-block'})
])

@app.callback(
    Output('table', 'data'),
    Output('count_lesson', 'children'),
    Input('graph', 'clickData')
)

def update_table(click_data):
    if click_data is None:
        return lesson_duration_new_table.to_dict('records'), f'Total count of lessons with too fast completion time: {num_unique_lessons.shape[0]}'
    else:
        selected_column_x = click_data['points'][0]['x']
        filtered_df = lesson_duration_new_table[lesson_duration_new_table['delta_seconds'] == selected_column_x].to_dict('records')
        selected_column_y = click_data['points'][0]['y']
        new_count = selected_column_y
        return filtered_df, f'Total count of lessons with too fast completion time: {new_count}'

if __name__ == '__main__':
    app.run_server(debug=True)