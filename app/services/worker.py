import logging
import os
import json
from app.core.celery_app import celery_app
from app.services.core_mapping.category_workflow import CategoryMappingWorkflow
from app.services.providers.factory import ProviderFactory
from app.services.core_mapping.attribute_option_workflow import AttributeOptionWorkflow
from app.core.config import settings

logger = logging.getLogger(__name__)

@celery_app.task(name="run_attribute_option")
def run_attribute_option(task_id, provider, json_data_path, input_excel_path, shop_name, token):
    logger.info(f"--- [START ATTRIBUTE/OPTION TASK] --- ID: {task_id}, Provider: {provider}, Shop: {shop_name}")

    workflow = AttributeOptionWorkflow()
    try:
        result = workflow.run(task_id, provider, json_data_path, input_excel_path, shop_name, token)
    except Exception as e:
        logger.error(f"Greška u run_attribute_option: {str(e)}")
        raise e

    return result

@celery_app.task(bind=True, name="run_category_mapping_task")
def run_category_mapping_task(self, task_id, input_json_path, shop_name, provider):
    logger.info(f"--- [START CATEGORY TASK] --- ID: {task_id}, File: {shop_name}, Provider: {provider}")
    
    workflow = CategoryMappingWorkflow()
    
    try:
        result = workflow.run(
            input_json_path=input_json_path, 
            shop_name=shop_name.replace(".json", ""), 
            provider=provider
        )
    except Exception as exc:
        logger.error(f"Kritična greška u run_category_mapping_task: {str(exc)}")
        raise exc

    return result

@celery_app.task(name="fetch_provider_data_task")
def fetch_provider_data_task(provider, credentials, shop_name):
    provider_folder = provider.lower()
    logger.info(f"--- [START FETCH TASK] --- Shop: {shop_name}, Provider: {provider_folder}")
    
    try:
        provider = ProviderFactory.get_provider(provider, credentials)
        categories = provider.get_categories()
        
        if not categories:
            logger.warning(f"Nisu pronađene kategorije za {shop_name}")
            return {"status": "failed", "reason": "No categories found"}

        file_name = f"{shop_name}_cache.json"
        
        provider_dir = os.path.join(
            settings.BASE_DIR, 
            "data", 
            "cachedCategories", 
            provider_folder
        )
        
        file_path = os.path.join(provider_dir, file_name)
        
        os.makedirs(provider_dir, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(categories, f, indent=4, ensure_ascii=False)
            
        logger.info(f"--- [SUCCESS] --- Podaci sačuvani u: {file_path}")
        
        return {
            "status": "completed", 
            "shop": shop_name, 
            "provider": provider_folder,
            "count": len(categories),
            "file_path": file_path
        }

    except Exception as e:
        logger.error(f"Kritična greška u fetch_provider_data_task: {str(e)}")
        return {"status": "error", "message": str(e)}

@celery_app.task(name="fetch_attribute_options_task")
def fetch_attribute_options_task(provider_type, credentials, shop_name):
    provider_folder = provider_type.lower()
    logger.info(f"--- [START ATTRIBUTE/OPTION FETCH TASK] --- Shop: {shop_name}, Provider: {provider_folder}")
    
    try:
        provider = ProviderFactory.get_provider(provider_type, credentials)
        attributes_options = provider.get_shop_structure()
        
        if not attributes_options:
            logger.warning(f"Nisu pronađeni atributi/opcije za {shop_name}")
            return {"status": "failed", "reason": "No attributes/options found"}

        file_name = f"{shop_name}_attributes_options.json"
        
        provider_dir = os.path.join(
            settings.BASE_DIR, 
            "data", 
            "cachedAttributesOptions", 
            provider_folder
        )
        
        file_path = os.path.join(provider_dir, file_name)
        
        os.makedirs(provider_dir, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(attributes_options, f, indent=4, ensure_ascii=False)
            
        logger.info(f"--- [SUCCESS] --- Atributi i opcije sačuvani u: {file_path}")
        
        return {
            "status": "completed", 
            "shop": shop_name, 
            "provider": provider_folder,
            "count": len(attributes_options),
            "file_path": file_path
        }

    except Exception as e:
        logger.error(f"Kritična greška u fetch_atribute_options_task: {str(e)}")
        return {"status": "error", "message": str(e)}