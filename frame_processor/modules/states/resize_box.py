
# 
def resize_box(x1, y1, x2, y2, resize_percent):
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    # Размеры
    width = x2 - x1
    height = y2 - y1

    scale = 1 + (resize_percent / 100.0)

    new_width = width * scale
    new_height = height * scale

    new_x1 = int(cx - new_width / 2)
    new_y1 = int(cy - new_height / 2)
    new_x2 = int(cx + new_width / 2)
    new_y2 = int(cy + new_height / 2)

    return new_x1, new_y1, new_x2, new_y2