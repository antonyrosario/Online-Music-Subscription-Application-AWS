import boto3

def create_music_table(dynamodb=None):
    dynamodb = boto3.client('dynamodb', region_name = 'us-east-1')

    # Define table schema
    table_name = 'music'
    attribute_definitions = [
        {'AttributeName': 'title', 'AttributeType': 'S'},
        {'AttributeName': 'artist', 'AttributeType': 'S'}
    ]
    key_schema = [
        {'AttributeName': 'title', 'KeyType': 'HASH'},
        {'AttributeName': 'artist', 'KeyType': 'RANGE'}
    ]
    provisioned_throughput = {'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10}

    # Create table
    table = dynamodb.create_table(
        TableName=table_name,
        AttributeDefinitions=attribute_definitions,
        KeySchema=key_schema,
        ProvisionedThroughput=provisioned_throughput
    )
    return table

if __name__ == '__main__':
    # Create login table
    music_table = create_music_table()
    print("Music table created:", music_table)
