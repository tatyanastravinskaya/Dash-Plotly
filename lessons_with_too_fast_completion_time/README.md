# Analysis of the speed of passing lessons by students

## Data

There are tables:

**finished_lesson_test** - table with lessons. Each row belongs to particular student who passed particular lesson of particular profession. Table fields:
** date_created - student completion time;
** id - unique ID of each row;
** lesson_id - foreign key for making a connection with table *lesson_index_test*;
** user_id - student ID.

**lesson_index_test** - table with all available lessons. Table fields:
* lesson_id - key field;
* lesson_name - lesson name;
* profession_id - profession ID for specific lesson;
* profession_name - profession name.

Each lesson could be passed by student only once. Student can pass lessons from different professions.

## Task
After rolling out the latest platform update, there is a bug: sometimes some lessons are passed by students too fast. Problem cases are: when no more than five seconds elapsed between the passage of two lessons of the program by the student.
First we need to limit to one cohort of a particular profession. The upload should only contain data for data-analyst students in the April 2020 cohort. The upload should not take the lessons of other cohorts or the lessons of this cohort, but in other professions. The April 2020 data-analyst cohort includes those students who completed their first lesson in the profession in April 2020.

**Purpose of analysis**:
* to see how many lessons were passed too fast;
* to make an interactive dashboard.

## Libraries

* *pandas*;
* *plotly*;
* *dash*.
