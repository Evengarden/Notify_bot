import datetime

month_dict = dict(января=1, февраля=2, марта=3, апреля=4, мая=5, июня=6, июля=7, августа=8, сентября=9, октября=10,
                  ноября=11, декабря=12)
day_dict = dict(сегодня=datetime.date.today(), завтра=datetime.date.today() + datetime.timedelta(days=1))
