import unicodedata
import re

def format_period(period_value: str) -> tuple[int, int]:
    text = str(period_value)
    return int(text[:4]), int(text[4:6])


def normalize_ubigeo(ubigeo_value) -> str:
    return str(ubigeo_value).zfill(6)


def transform_client_state(raw_state: str) -> str:
    if not raw_state:
        return None

    normalized = raw_state.strip().upper()

    mapping = {
        "NORMAL": "NO",
        "ANULADO": "AN"
    }
    return mapping.get(normalized, None)


def clean_text(value: str) -> str:
    if not isinstance(value, str):
        return value

    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii", "ignore")
    value = re.sub(r"[^A-Z0-9\s]", "", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip().upper()
