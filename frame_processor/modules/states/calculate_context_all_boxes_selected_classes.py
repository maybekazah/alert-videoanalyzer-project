from modules.nn_functions.calculation import CalculationFunctions
calculation_functions = CalculationFunctions()


def calculate_context_all_boxes_selected_classes(context, detect_boxes_with_classes):
    context['list_all_detect_boxes'] = calculation_functions.get_list_of_all_detect_boxes_service(
        detect_boxes_with_classes,
        context['list_of_detect_classes']
    )
