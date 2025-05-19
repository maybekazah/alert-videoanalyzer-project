import datetime


def use_day_night_contours(context):
    if context['use_night_countour']:
        now = datetime.datetime.now().time().replace(microsecond=0)
        night_countour_time_start = datetime.time(*context['night_countour_time_start'])
        night_countour_time_end = datetime.time(*context['night_countour_time_end'])

        if night_countour_time_start < night_countour_time_end:
            is_night_time = night_countour_time_start <= now < night_countour_time_end
        else:
            is_night_time = now >= night_countour_time_start or now < night_countour_time_end

        if is_night_time:
            context['contour_points_list'] = context['night_contour']

    if context['use_day_countour']:
        now = datetime.datetime.now().time().replace(microsecond=0)
        
        day_countour_time_start = datetime.time(*context['day_countour_time_start'])
        day_countour_time_end = datetime.time(*context['day_countour_time_end'])

        if day_countour_time_start < day_countour_time_end:
            is_day_time = day_countour_time_start <= now < day_countour_time_end
        else:
            is_day_time = now >= day_countour_time_start or now < day_countour_time_end

        if is_day_time:
            context['contour_points_list'] = context['day_contour']
