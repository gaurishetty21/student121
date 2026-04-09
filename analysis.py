import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json

SUBJECTS = ['math_score', 'physics_score', 'chemistry_score', 'english_score', 'cs_score']
SUBJECT_LABELS = ['Math', 'Physics', 'Chemistry', 'English', 'CS']

def load_data():
    df = pd.read_csv("data/students.csv")
    df['avg_score'] = df[SUBJECTS].mean(axis=1).round(2)
    df['total_score'] = df[SUBJECTS].sum(axis=1)
    df['grade'] = df['avg_score'].apply(assign_grade)
    df['status'] = df['avg_score'].apply(lambda x: 'Pass' if x >= 50 else 'Fail')
    df['performance_band'] = df['avg_score'].apply(performance_band)
    return df

def assign_grade(avg):
    if avg >= 90: return 'A+'
    elif avg >= 80: return 'A'
    elif avg >= 70: return 'B'
    elif avg >= 60: return 'C'
    elif avg >= 50: return 'D'
    else: return 'F'

def performance_band(avg):
    if avg >= 85: return 'Outstanding'
    elif avg >= 70: return 'Good'
    elif avg >= 55: return 'Average'
    else: return 'Needs Improvement'

def get_summary(df):
    return {
        "total_students": int(len(df)),
        "avg_score": float(round(df["avg_score"].mean(), 2)),
        "pass_rate": float(round((df["avg_score"] >= 50).mean() * 100, 1)),
        "top_performer": df.loc[df["avg_score"].idxmax(), "name"],
        "top_score": float(round(df["avg_score"].max(), 2)),
        "lowest_score": float(round(df["avg_score"].min(), 2)),
        "median_score": float(round(df["avg_score"].median(), 2)),
        "std_dev": float(round(df["avg_score"].std(), 2)),
        "grade_a_count": int((df["grade"].isin(['A+', 'A'])).sum()),
        "fail_count": int((df["grade"] == 'F').sum()),
        "avg_attendance": float(round(df["attendance"].mean(), 1)),
        "departments": int(df["department"].nunique()),
        "female_count": int((df["gender"] == 'F').sum()),
        "male_count": int((df["gender"] == 'M').sum()),
    }

def chart_layout():
    return dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.03)',
        font=dict(color='white', family='DM Sans, sans-serif'),
        title_font=dict(size=16, color='#a5b4fc'),
        legend=dict(bgcolor='rgba(0,0,0,0.3)', bordercolor='rgba(255,255,255,0.1)', borderwidth=1),
        xaxis=dict(gridcolor='rgba(255,255,255,0.07)', linecolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.07)', linecolor='rgba(255,255,255,0.1)'),
        margin=dict(t=50, b=30, l=30, r=30)
    )

def score_distribution_chart(df):
    fig = px.histogram(df, x="avg_score", nbins=15,
                       color_discrete_sequence=["#00d4ff"],
                       title="Score Distribution")
    fig.update_layout(**chart_layout())
    fig.update_traces(marker_line_color="#00ffcc", marker_line_width=1.5)
    return fig.to_json()

def subject_avg_bar(df):
    means = df[SUBJECTS].mean().round(2)
    colors = ["#00d4ff","#a78bfa","#34d399","#fb923c","#f472b6"]
    fig = go.Figure(go.Bar(
        x=SUBJECT_LABELS, y=means.values,
        marker_color=colors,
        text=means.values,
        textposition='outside',
        textfont=dict(color='white', size=13)
    ))
    fig.update_layout(title="Average Score by Subject", **chart_layout())
    return fig.to_json()

def grade_distribution_chart(df):
    grade_order = ['A+','A','B','C','D','F']
    counts = df['grade'].value_counts().reindex(grade_order, fill_value=0)
    colors = ["#00ffcc","#00d4ff","#a78bfa","#fb923c","#fbbf24","#f87171"]
    fig = go.Figure(go.Bar(
        x=counts.index, y=counts.values,
        marker_color=colors,
        text=counts.values,
        textposition='outside',
        textfont=dict(color='white', size=13)
    ))
    fig.update_layout(title="Grade Distribution", **chart_layout())
    return fig.to_json()

def attendance_vs_score_chart(df):
    color_map = {'A+':'#00ffcc','A':'#00d4ff','B':'#a78bfa','C':'#fb923c','D':'#fbbf24','F':'#f87171'}
    fig = px.scatter(df, x="attendance", y="avg_score",
                     color="grade", hover_data=["name","department"],
                     color_discrete_map=color_map,
                     title="Attendance vs Performance",
                     trendline="ols")
    fig.update_layout(**chart_layout())
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color='white')))
    return fig.to_json()

def dept_comparison_chart(df):
    dept_avg = df.groupby('department')[SUBJECTS].mean().round(2)
    fig = go.Figure()
    colors = ["#00d4ff","#a78bfa","#34d399","#fb923c","#f472b6"]
    for i, subj in enumerate(SUBJECTS):
        fig.add_trace(go.Bar(name=SUBJECT_LABELS[i], x=dept_avg.index, y=dept_avg[subj],
                             marker_color=colors[i]))
    fig.update_layout(barmode='group', title="Department-wise Subject Performance", **chart_layout())
    return fig.to_json()

def gender_performance_chart(df):
    gender_avg = df.groupby('gender')['avg_score'].mean().round(2)
    fig = go.Figure(go.Pie(
        labels=['Male' if g=='M' else 'Female' for g in gender_avg.index],
        values=gender_avg.values,
        hole=0.5,
        marker_colors=["#00d4ff","#f472b6"],
        textfont=dict(color='white', size=14)
    ))
    fig.update_layout(title="Gender-wise Average Score", **chart_layout())
    return fig.to_json()

def study_hours_chart(df):
    fig = px.scatter(df, x="study_hours_per_day", y="avg_score",  # ← changed
                     color="performance_band",
                     size="attendance",
                     hover_data=["name"],
                     title="Study Hours vs Performance",
                     color_discrete_map={
                         'Outstanding':'#00ffcc',
                         'Good':'#00d4ff',
                         'Average':'#fbbf24',
                         'Needs Improvement':'#f87171'
                     })
    fig.update_layout(**chart_layout())
    return fig.to_json()

def correlation_heatmap(df):
    # Only use columns that actually exist in your CSV
    available = [c for c in ['attendance','study_hours_per_day','avg_score'] + SUBJECTS
                 if c in df.columns]
    labels_map = {
        'math_score':'Math','physics_score':'Physics','chemistry_score':'Chemistry',
        'english_score':'English','cs_score':'CS',
        'attendance':'Attendance','study_hours_per_day':'Study Hrs','avg_score':'Avg Score'
    }
    labels = [labels_map.get(c, c) for c in available]
    corr = df[available].corr().round(2)
    fig = go.Figure(go.Heatmap(
        z=corr.values, x=labels, y=labels,
        colorscale=[[0,'#1a0533'],[0.5,'#4f46e5'],[1,'#00ffcc']],
        text=corr.values.round(2),
        texttemplate="%{text}",
        showscale=True
    ))
    fig.update_layout(title="Correlation Heatmap", **chart_layout(), height=500)
    return fig.to_json()

# Line ~170 — top_students_table function
def top_students_table(df):
    top = df.nlargest(10, 'avg_score')[['name','department','avg_score','grade',
                                        'attendance','study_hours_per_day']].copy()  # ← changed
    top.columns = ['Name','Dept','Avg Score','Grade','Attendance %','Study Hrs/Day']
    return top.to_dict(orient='records')

# Line ~177 — bottom_students_table function
def bottom_students_table(df):
    bot = df.nsmallest(10, 'avg_score')[['name','department','avg_score','grade',
                                          'attendance','study_hours_per_day']].copy()  # ← changed
    bot.columns = ['Name','Dept','Avg Score','Grade','Attendance %','Study Hrs/Day']
    return bot.to_dict(orient='records')

def radar_chart_dept(df):
    depts = df['department'].unique()
    fig = go.Figure()
    colors = ["#00d4ff","#a78bfa","#34d399","#fb923c","#f472b6"]
    for i, dept in enumerate(depts):
        sub = df[df['department']==dept][SUBJECTS].mean().values.tolist()
        sub += sub[:1]
        fig.add_trace(go.Scatterpolar(
            r=sub, theta=SUBJECT_LABELS + [SUBJECT_LABELS[0]],
            fill='toself', name=dept,
            line_color=colors[i % len(colors)],
            opacity=0.7
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,100],
                            gridcolor='rgba(255,255,255,0.1)', color='white'),
            angularaxis=dict(color='white')
        ),
        title="Radar: Department Subject Strengths",
        **chart_layout()
    )
    return fig.to_json()

def income_vs_performance(df):
    # Using parent_education as proxy for income level
    education_order = ['High School', 'Graduate', 'Postgraduate']
    income_avg = df.groupby('parent_education')['avg_score'].mean().reindex(education_order).round(2)
    fig = go.Figure(go.Bar(
        x=income_avg.index, y=income_avg.values,
        marker_color=["#f87171","#fbbf24","#34d399"],
        text=income_avg.values, textposition='outside',
        textfont=dict(color='white', size=13)
    ))
    fig.update_layout(title="Parent Education vs Avg Score", **chart_layout())
    return fig.to_json()

def part_time_impact(df):
    pt = df.groupby('part_time_job')['avg_score'].mean().round(2)
    fig = go.Figure(go.Bar(
        x=['No Part-time Job' if x=='No' else 'Has Part-time Job' for x in pt.index],
        y=pt.values,
        marker_color=["#00d4ff","#f87171"],
        text=pt.values, textposition='outside',
        textfont=dict(color='white', size=14)
    ))
    fig.update_layout(title="Impact of Part-time Job on Scores", **chart_layout())
    return fig.to_json()

def dept_summary_table(df):
    dept = df.groupby('department').agg(
        Students=('name','count'),
        Avg_Score=('avg_score', lambda x: round(x.mean(),2)),
        Pass_Rate=('status', lambda x: round((x=='Pass').mean()*100,1)),
        Avg_Attendance=('attendance', lambda x: round(x.mean(),1)),
        Top_Scorer=('avg_score', 'max')
    ).reset_index()
    dept.columns = ['Department','Students','Avg Score','Pass Rate %','Avg Attendance','Top Score']
    return dept.to_dict(orient='records')

def get_all_students(df):
    return df[['name','department','avg_score','grade','attendance','study_hours_per_day']].to_dict(orient='records')