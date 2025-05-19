from modules.nn_functions.calculation import CalculationFunctions
calculation_functions = CalculationFunctions()


def get_detection_data_all_selected_classes(context, detect_boxes_with_classes):
    context['detection_model_result'] = calculation_functions.get_data_detection_result_service(
        detect_boxes_with_classes,
        context['list_of_detect_classes']
        )
