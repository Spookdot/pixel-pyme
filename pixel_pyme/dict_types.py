from typing import TypedDict

Position = TypedDict('Position', {
    'box_left': int, 'box_top': int, 'box_right': int, 'box_bottom': int, 'id': int, 'parameter_id': int
})

Parameter = TypedDict('Parameter', {
    'id': int, 'meme_id': int, 'name': str, 'position': list[Position]
})

MemeData = TypedDict('MemeData', {
    "id": int, "name": str, "image_url": str, "parameter": list[Parameter]
})

ShortMemeData = TypedDict("ShortMemeData", {
    "id": int, "name": str, "image_url": str, "creator_id": str, "server_id": str
})
