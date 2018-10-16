import json
import boto3
from datetime import datetime, timedelta

ec2 = boto3.resource( 'ec2' )
s3 = boto3.resource( 's3' )

##
# Event data:
# {
#   "serviceName": "mytag1",
#   "bucket": "kstest-bucket-1"
# }
##

def lambda_handler( event, context ):
    instances = findInstances( event.get( 'serviceName' ) )
    results = json.dumps( { "results": instances } )
    
    response = {}
    
    if results:
        bucket = event.get( 'bucket' )
        store( results, bucket )
        
    
def findInstances( serviceName ):
    filters = [
        {
            'Name': 'instance-state-name',
            'Values': [ 'running' ]
        },
        {
            'Name': 'tag:Name',
            'Values': [ serviceName ]
        }
    ]
    
    instances = ec2.instances.filter(
        Filters = filters
    )
    
    results = []
    
    if instances:
        for instance in instances:
            instanceAge = ( datetime.now( instance.launch_time.tzinfo ) - instance.launch_time )
    
            if instanceAge.days > 30:
                results.append( {
                    "instance_id": instance.instance_id,
                    "service_name": serviceName,
                    "launch_time": str(instance.launch_time),
                    "age": instanceAge.days
                } )
    
    return results
    
    
def store( data, bucketName, region='' ):
    if not region:
        region = 'eu-west-1'
        
    filename = 'instances-export_' + datetime.now().strftime( "%y-%m-%d-%H-%M-%S" ) + '.json'
    
    bucket = s3.Bucket( bucketName )
    
    s3.Object( bucketName, filename ).put( Body = data )