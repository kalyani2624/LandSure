import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def find_spatial_neighbors(
    target_bbox: List[int],
    candidate_boxes: List[Dict[str, Any]],
    direction: str = "right",
    max_distance_px: int = 400
) -> List[Dict[str, Any]]:
    """
    Finds bounding boxes positioned immediately to the right or below a target label bounding box.
    target_bbox: [x, y, w, h]
    """
    tx, ty, tw, th = target_bbox
    t_center_y = ty + (th / 2.0)
    t_center_x = tx + (tw / 2.0)
    t_right = tx + tw
    t_bottom = ty + th

    matches = []
    for cand in candidate_boxes:
        c_bbox = cand.get("bbox", [0, 0, 0, 0])
        cx, cy, cw, ch = c_bbox
        c_center_y = cy + (ch / 2.0)
        c_center_x = cx + (cw / 2.0)

        if direction == "right":
            # Must be to the right of the target and vertically aligned
            if cx >= (t_right - 10) and (cx - t_right) <= max_distance_px:
                if abs(c_center_y - t_center_y) <= max(th * 1.2, 25):
                    matches.append(cand)
        elif direction == "below":
            # Must be below the target and horizontally aligned
            if cy >= (t_bottom - 10) and (cy - t_bottom) <= max_distance_px:
                if abs(c_center_x - t_center_x) <= max(tw * 1.5, 120):
                    matches.append(cand)

    return matches
