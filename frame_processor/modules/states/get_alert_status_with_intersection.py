from modules.nn_functions.calculation import CalculationFunctions
calculation_functions = CalculationFunctions()


def get_alert_status_with_intersection(context):
    if context['detect_with_perimeter_intersection']:
        context['alert_status'] = calculation_functions.get_alert_for_any_box_intersecting_service(
            context['list_all_detect_boxes'],
            context['contour_points_list'],
            context['resize_detection_boxes']
            )