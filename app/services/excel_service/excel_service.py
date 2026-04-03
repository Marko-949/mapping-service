import pandas as pd
import logging
import os
from pathlib import Path
logger = logging.getLogger(__name__)

def read_input_plan(temp_file_path: str):
    if not os.path.exists(temp_file_path):
        logger.error(f"Fajl nije pronađen: {temp_file_path}")
        return []
    
    df = pd.read_excel(temp_file_path)

    data_list = df.to_dict('records')
    
    logger.info(f"Učitano {len(data_list)} redova za mapiranje iz Excela.")
    return data_list

def save_final_mapping(results: list, output_path: str):
    if not results:
        return None
    
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(results)
    desired_cols = ["TypeFrom", "ExternalKey", "TypeTo", "InternalKey"]
    existing_cols = [c for c in desired_cols if c in df.columns]
    
    df[existing_cols].to_excel(output_path, index=False)
    return output_path