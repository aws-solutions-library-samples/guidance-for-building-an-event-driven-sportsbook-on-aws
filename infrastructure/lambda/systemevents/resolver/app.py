from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import AppSyncResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

tracer = Tracer()
logger = Logger()
app = AppSyncResolver()

@app.resolver(type_name="Mutation", field_name="addSystemEvent")
@tracer.capture_method
def add_system_event(input: dict) -> dict:
    """
    Add a system event to the database.
    
    This is a simple echo resolver that returns the input as if it was written to a data store.
    In a production environment, this would typically write to a database.
    
    Args:
        input: The system event input data
        
    Returns:
        The system event with typename
    """
    try:
        return {'__typename': 'SystemEvent', **input}
    except Exception as e:
        logger.error(f"Error adding system event: {str(e)}")
        return {'__typename': 'Error', 'message': 'Failed to add system event'}


@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """
    Main Lambda handler function.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        AppSync resolver response
    """
    try:
        return app.resolve(event, context)
    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        return {"errors": [{"message": "Internal server error"}]}
