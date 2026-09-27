import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def parse_tabular_layout(lines: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Groups OCR lines into geometric rows based on vertical centroid clustering.
    Enables table extraction across Indian land ledgers (Adangal, Khatiyan).
    """
    if not lines:
        return {"rows": [], "has_tables": False}

    # Sort lines top-to-bottom, left-to-right
    sorted_lines = sorted(lines, key=lambda item: (item.get("bbox", [0, 0, 0, 0])[1], item.get("bbox", [0, 0, 0, 0])[0]))

    rows = []
    current_row = []
    current_y = -1
    row_height = 20

    for item in sorted_lines:
        bbox = item.get("bbox", [0, 0, 0, 0])
        y = bbox[1]
        h = max(bbox[3], 15)

        if current_y == -1 or abs(y - current_y) <= (row_height * 0.75):
            current_row.append(item)
            current_y = y
            row_height = h
        else:
            if current_row:
                # Sort row elements left-to-right
                current_row.sort(key=lambda it: it.get("bbox", [0, 0, 0, 0])[0])
                rows.append(current_row)
            current_row = [item]
            current_y = y
            row_height = h

    if current_row:
        current_row.sort(key=lambda it: it.get("bbox", [0, 0, 0, 0])[0])
        rows.append(current_row)

    return {
        "rows": rows,
        "row_count": len(rows),
        "has_tables": len(rows) > 3
    }
