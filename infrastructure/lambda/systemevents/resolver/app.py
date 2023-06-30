
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
    # echo response as if we wrote it to data store
    logger.info(input)
    return {'__typename': 'SystemEvent', **input}

@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)