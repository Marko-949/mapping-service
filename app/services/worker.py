import logging
from app.core.celery_app import celery_app
from app.services.woo_attributes_options_mapping_service.mapping_service import WooAttributesOptionsMappingService
from app.services.categories_mapping_service.mapping_service import CategoriesMappingService
from app.services.core_mapping.category_workflow import CategoryMappingWorkflow
from app.services.providers.factory import ProviderFactory
from app.services.core_mapping.attribute_option_workflow import AttributeOptionWorkflow

logger = logging.getLogger(__name__)

@celery_app.task(name="run_attribute_option")
def run_attribute_option(task_id, provider_type, credentials, file_path, token, shop_name):
    logger.info(f"--- [START ATTRIBUTE/OPTION TASK] --- ID: {task_id}, Provider: {provider_type}, Shop: {shop_name}")

    provider = ProviderFactory.get_provider(provider_type, credentials)
    workflow = AttributeOptionWorkflow()
    try:
        result = workflow.run(task_id, provider, file_path, token, shop_name)
    except Exception as e:
        logger.error(f"Greška u run_attribute_option: {str(e)}")
        raise e

    return result

@celery_app.task(bind=True, name="run_category_mapping_task")
def run_category_mapping_task(self, task_id, input_file_path, file_name, source_type):
    logger.info(f"--- [START CATEGORY TASK] --- ID: {task_id}, File: {file_name}, Source: {source_type}")
    
    workflow = CategoryMappingWorkflow()
    
    try:
        result = workflow.run(
            input_json_path=input_file_path, 
            shop_name=file_name.replace(".json", ""), 
            source_type=source_type
        )
    except Exception as exc:
        logger.error(f"Kritična greška u run_category_mapping_task: {str(exc)}")
        raise exc

    return result
