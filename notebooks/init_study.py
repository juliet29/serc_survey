import marimo

__generated_with = "0.18.1"
app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path
    from datetime import date

    import marimo as mo 

    import polars as pl 
    import polars.selectors as cs
    import altair as alt
    return Path, alt, cs, date, mo, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Read in data
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Declare path where the csv is located. I renamed the file to something a bit simpler to type. You will need to change the path to where you have saved the file.
    """)
    return


@app.cell
def _(Path):
    survey_path = Path.cwd() / "static/_01_inputs/survey251117.csv"
    survey_path 
    return (survey_path,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Read in the data using [polars](https://docs.pola.rs/). Here, I am skipping the first two rows after the headers. The file has two "types" of columns: columns for metadata, and columns pertaining to the actual questions. In the case of the metadata columns, the headers are repeated. In the case of the columns with actual questions, the first row contains the question, where as the header just has the question number. You can see the questions by removing the `skip_rows_after_header` parameter from the function call.
    """)
    return


@app.cell
def _(pl, survey_path):
    df = pl.read_csv(survey_path,skip_rows_after_header=2)
    df
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Study data related to questions
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Here, I am making a dataframe that has just the columns pertaining to the questions. To do this, I `match` columns starting with `Q` followed by a number (represented as `\d`). Some further filtering has to be done because many of the columns do not contain relevant information..
    """)
    return


@app.cell
def _(cs, df):
    dfqs = df.select(cs.matches("Q\d"))
    dfqs
     # TODO get questions as dict mapping question numbers to actual questions ; then drop those with invalid answers.. 
    return (dfqs,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Here, I am looking at the unique emails. You can see that some are likely invalid.
    """)
    return


@app.cell
def _(dfqs):
    dfqs.select("Q7.5_4").unique()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Study questions related to metadata
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Here, I am getting the columns related to metadata by getting those that are *not* related to questions. I then add a column to calculate the time spent on the survey in minutes and change all datetime columns to be in the correct datetime format.
    """)
    return


@app.cell
def _(cs, df, pl):
    datetime_format = "%m/%d/%Y %H:%M"
    dfmeta = df.select(~cs.matches("Q\d")).with_columns(
        pl.duration(seconds=pl.col("Duration (in seconds)"))
        .dt.total_minutes(fractional=True)
        .alias("duration_mins"),
        pl.col("StartDate").str.to_datetime(datetime_format),
        pl.col("EndDate").str.to_datetime(datetime_format),
         pl.col("RecordedDate").str.to_datetime(datetime_format)

    )
    dfmeta
    return (dfmeta,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Histogram of minutes spent on survey.
    """)
    return


@app.cell
def _(alt, dfmeta):
    chart = (
        alt.Chart(dfmeta)
        .mark_bar()
        .encode(alt.X("binned_duration_mins:O").title("Binned Minutes"), alt.Y("count()")).transform_bin("binned_duration_mins", field="duration_mins", bin={"step":0.5})
    )
    chart.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Histogram of dates when survey responses were recorded.
    """)
    return


@app.cell
def _(alt, dfmeta):
    c2 = (
        alt.Chart(dfmeta)
        .mark_bar()
        .encode(alt.X("monthdate(StartDate):O"), alt.Y("count()"))
    )
    c2.show()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Filter to dates where most survey responses were observed
    """)
    return


@app.cell
def _(date, dfmeta, pl):

    dfprime = dfmeta.filter(
    pl.col("StartDate").is_between(date(2025, 11, 11), date(2025, 11, 16))).sort(by="StartDate")
    dfprime


    return (dfprime,)


@app.cell
def _(mo):
    mo.md(r"""
    ### Start date and time vs duration in minutes
    """)
    return


@app.cell
def _(alt, dfprime):

    (
        alt.Chart(dfprime)
        .mark_point()
        .encode(
            x=alt.X(field='StartDate', type='nominal',),
            y=alt.Y(field='duration_mins', type='quantitative', bin={
                'step': 0.1
            }),
            tooltip=[
                alt.Tooltip(field='StartDate', title='StartDate'),
                alt.Tooltip(field='duration_mins', format=',.2f', bin={
                    'step': 0.1
                })
            ]
        )
        .properties(
            height=290,
            width='container',
            config={
                'axis': {
                    'grid': False
                }
            }
        )
    )

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Start date and time vs duration in Recaptcha scores
    """)
    return


@app.cell
def _(alt, dfprime):
    (
        alt.Chart(dfprime)
        .mark_point()
        .encode(
            x=alt.X(field='StartDate', type='nominal'),
            y=alt.Y(field='Q_RecaptchaScore', type='quantitative'),
            tooltip=[
                alt.Tooltip(field='StartDate'),
                alt.Tooltip(field='Q_RecaptchaScore', format=',.2f')
            ]
        )
        .properties(
            height=290,
            width='container',
            config={
                'axis': {
                    'grid': True
                }
            }
        )
    )

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Histogram of duration of time spent on survey, faceted by date
    """)
    return


@app.cell
def _(alt, dfprime):


    (
        alt.Chart(dfprime)
        .mark_bar()
        .encode(
            alt.X("binned_duration_mins:O").title("Binned Minutes"),
            alt.Y("count()"),
            alt.Row("monthdate(StartDate)")
        )
        .transform_bin(
            "binned_duration_mins", field="duration_mins", bin={"step": 0.5}
        )
        .properties(width=600, height=100)
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Histogram of duration of time spent on survey (in seconds), faceted by date

    Looking at seconds allows us to see the data more clearly, and understand if there are overlaps. There is some evidence of surveys having almost the same duration, even if the the number of seconds is slightly different. Here, have also removed the outlier.
    """)
    return


@app.cell
def _(alt, dfprime, pl):
    DURCOL = "Duration (in seconds)"

    (
        alt.Chart(dfprime.filter(pl.col(DURCOL)< 2000))
        .mark_bar()
        .encode(
            alt.X(DURCOL).title("Seconds to Complete"),
            alt.Y("count()"),
            alt.Row("monthdate(StartDate)")
        )
        .properties(width=600, height=100)
    )
    return (DURCOL,)


@app.cell
def _(mo):
    mo.md(r"""
    ### Histogram of Recaptcha scores, faceted by date
    """)
    return


@app.cell
def _(DURCOL, alt, dfprime, pl):

    (
        alt.Chart(dfprime.filter(pl.col(DURCOL)< 2000))
        .mark_bar()
        .encode(
            alt.X("Q_RecaptchaScore").title("Q_RecaptchaScore"),
            alt.Y("count()"),
            alt.Row("monthdate(StartDate)")
        )
        .properties(width=600, height=100)
    )
    return


if __name__ == "__main__":
    app.run()
