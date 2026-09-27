from typing import Tuple, Optional

UNIT_TO_ACRES = {
    "acres": 1.0,
    "acre": 1.0,
    "guntas": 0.025,
    "gunta": 0.025,
    "guntha": 0.025,
    "hectares": 2.47105,
    "hectare": 2.47105,
    "sq yards": 0.000206612,
    "sq yard": 0.000206612,
    "cent": 0.01,
    "cents": 0.01,
    "bigha": 0.625,
    "biswa": 0.03125
}

def standardize_unit(raw_unit: Optional[str]) -> str:
    if not raw_unit:
        return "Acres"
    k = raw_unit.lower().strip()
    if "gunta" in k: return "Guntas"
    if "hectare" in k or "हेक्टेयर" in k or "హెక్టార్" in k: return "Hectares"
    if "sq yard" in k or "గజ" in k or "गज" in k: return "Sq Yards"
    if "cent" in k or "సెంట్" in k or "சென்ட்" in k: return "Cents"
    return "Acres"

def convert_area_unit(value: float, from_unit: str, to_unit: str = "Acres") -> float:
    if value is None or value <= 0:
        return 0.0
    from_key = (from_unit or "Acres").lower().strip()
    to_key = (to_unit or "Acres").lower().strip()
    
    factor_to_acres = UNIT_TO_ACRES.get(from_key, 1.0)
    value_in_acres = value * factor_to_acres
    
    factor_from_acres = 1.0 / UNIT_TO_ACRES.get(to_key, 1.0)
    return round(value_in_acres * factor_from_acres, 4)

convert_area = convert_area_unit
