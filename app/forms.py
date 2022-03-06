from wtforms import Form, SelectField


class SpotifyTimeSearchForm(Form):
    top_type = SelectField('Type', choices=[
        ('artists', 'Artists'),
        ('tracks', 'Tracks')
    ])
    time_range = SelectField('Time Range', choices=[
        ('short_term', 'Last 4 weeks'),
        ('medium_term', 'Last 6 months'),
        ('long_term', 'Long term')
    ])
