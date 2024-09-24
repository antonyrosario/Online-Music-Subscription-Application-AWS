import boto3


def create_login_table():

    dynamodb = boto3.client('dynamodb', region_name = 'us-east-1')
    # Define table schema
    table_name = 'login'
    attribute_definitions = [
        {'AttributeName': 'email', 'AttributeType': 'S'},
    ]
    key_schema = [
        {'AttributeName': 'email', 'KeyType': 'HASH'},
    ]
    provisioned_throughput = {'ReadCapacityUnits': 10, 'WriteCapacityUnits': 15}

    # Create table
    table = dynamodb.create_table(
        TableName=table_name,
        AttributeDefinitions=attribute_definitions,
        KeySchema=key_schema,
        ProvisionedThroughput=provisioned_throughput
    )

    # Wait for table to be created
    waiter = dynamodb.get_waiter('table_exists')
    waiter.wait(TableName=table_name)

    return table

def enter_user_credentials():
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')

    # Hardcoded email IDs, usernames, and passwords
    credentials = [
        {'email': 's39402030@student.rmit.edu.au', 'user_name': 'Antony Rosario0', 'password': '012345'},
        {'email': 's39402031@student.rmit.edu.au', 'user_name': 'Antony Rosario1', 'password': '123456'},
        {'email': 's39402032@student.rmit.edu.au', 'user_name': 'Antony Rosario2', 'password': '234567'},
        {'email': 's39402033@student.rmit.edu.au', 'user_name': 'Antony Rosario3', 'password': '345678'},
        {'email': 's39402034@student.rmit.edu.au', 'user_name': 'Antony Rosario4', 'password': '456789'},
        {'email': 's39402035@student.rmit.edu.au', 'user_name': 'Antony Rosario5', 'password': '567890'},
        {'email': 's39402036@student.rmit.edu.au', 'user_name': 'Antony Rosario6', 'password': '678901'},
        {'email': 's39402037@student.rmit.edu.au', 'user_name': 'Antony Rosario7', 'password': '789012'},
        {'email': 's39402038@student.rmit.edu.au', 'user_name': 'Antony Rosario8', 'password': '890123'},
        {'email': 's39402039@student.rmit.edu.au', 'user_name': 'Antony Rosario9', 'password': '901234'}
    ]

    # Put each item into the login table
    for credential in credentials:
        dynamodb.put_item(
            TableName='login',
            Item={
                'email': {'S': credential['email']},
                'user_name': {'S': credential['user_name']},
                'password': {'S': credential['password']}
            }
        )

if __name__ == '__main__':

    # Create login table
    login_table = create_login_table()
    print("Login table created:", login_table)

    # Enter user credentials into the login table
    enter_user_credentials()
    print("User credentials entered into the login table.")
