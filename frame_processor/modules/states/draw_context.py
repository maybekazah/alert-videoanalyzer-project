from modules.nn_functions.visualization import VisualizationFunctions
visualization_functions = VisualizationFunctions()


def draw_context(context, detect_boxes, detect_boxes_with_classes):
    if context['draw_result']:
        if context['draw_detect_boxes']:

            context['frame'] = visualization_functions.draw_detection_model_result_without_plot_service(
                context['frame'],
                detect_boxes_with_classes,
                context['list_of_detect_classes'], 
                context['box_color'],
                context['draw_line_thickless']
                )    


        if context['draw_perimeter']:
            context['frame'] = visualization_functions.draw_day_night_contour_service(
                context['frame'],
                context['contour_points_list'],
                context['countour_color'],
                context['draw_line_thickless']
                )
