from config.settings import CITIES
from src.extractor import extract_all
from src.transformer import transform_all
from src.loader import load
from src.logger import get_logger

logger = get_logger("pipeline")

def run():
    logger.info("=== Pipeline starting ===")

    # Extract
    raw = extract_all(CITIES)
    logger.info(f"Extracted data for {len(raw)} cities")

    # Transform
    df = transform_all(raw)
    logger.info(f"Total rows after transform: {len(df)}")

    # Load
    rows_loaded = load(df)

    # Summary report
    print("\n===== Pipeline Summary =====")
    print(f"Cities processed : {df['city'].nunique()}")
    print(f"Total rows loaded: {rows_loaded}")
    print(f"Avg temperature  : {df['temperature_c'].mean():.1f}°C")
    print(f"Max windspeed    : {df['windspeed_kmh'].max():.1f} km/h")
    print(f"Rainy hours      : {(df['precipitation_mm'] > 0).sum()}")
    print("============================\n")

    logger.info("=== Pipeline finished ===")

if __name__ == "__main__":
    run()