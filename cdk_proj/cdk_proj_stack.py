from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_dms as dms
)
from constructs import Construct
import aws_cdk as cdk

class CdkProjStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        replication_instance = dms.CfnReplicationInstance(self, "MyCdkReplicationInstance",
                replication_instance_identifier='cdk-deployed-repl-instance',
                replication_instance_class='dms.t3.micro',
                allocated_storage=50,
                engine_version='3.5.2'
                )

        cfn_endpoint = dms.CfnEndpoint(self, "MySourceEndpoint",
                                       endpoint_type='source',
                                       engine_name='aurora',
                                       endpoint_identifier='cdk-deployed-aurora-source-endpoint',
                                       server_name='', # mysql server  url
                                       port=3306, 
                                       username='', # login
                                       password='' # password
                                       ) 
        target_endpoint = dms.CfnEndpoint(self, 'MyTargetEndpoint',
                                          endpoint_type='target',
                                          engine_name='dynamodb',
                                          endpoint_identifier='cdk-deployed-dynamo-target-endpoint',
                                          dynamo_db_settings=dms.CfnEndpoint.DynamoDbSettingsProperty(
                                              service_access_role_arn='arn:aws:iam::922425785232:role/iam-dms-dynamodb-role'
                                              )
                                          )
        table_mapping_json = '''{
        "rules": [
            {
                "rule-type": "selection",
                "rule-id": "097157240",
                "rule-name": "097157240",
                "object-locator": {
                    "schema-name": "test_schema",
                    "table-name": "test_table"
                },
                "rule-action": "include",
                "filters": []
            },
            {
                "rule-type": "selection",
                "rule-id": "097157247",
                "rule-name": "097157247",
                "object-locator": {
                    "schema-name": "test_schema",
                    "table-name": "test_table_values"
                },
                "rule-action": "include",
                "filters": []
            }
        ]
}'''
        replication_task = dms.CfnReplicationTask(self, 'MyCdkRepolicationTask',
                                                  migration_type='full-load-and-cdc',
                                                  source_endpoint_arn=cfn_endpoint.ref,
                                                  target_endpoint_arn=target_endpoint.ref,
                                                  replication_instance_arn=replication_instance.ref,
                                                  table_mappings=table_mapping_json

                )

        #bucket = s3.Bucket(self, "MyFirstBucket",
        #    removal_policy=cdk.RemovalPolicy.DESTROY)

