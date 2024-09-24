import uuid

import boto3

dynamodb = boto3.client('dynamodb', region_name='us-east-1')


def create_subscription_table():
    table_name = 'subscription'
    attribute_definitions = [
        {'AttributeName': 'subid', 'AttributeType': 'S'},  # Change AttributeType to 'S' for string
        {'AttributeName': 'email', 'AttributeType': 'S'}
    ]
    key_schema = [
        {'AttributeName': 'subid', 'KeyType': 'HASH'},
        {'AttributeName': 'email', 'KeyType': 'RANGE'}
    ]
    provisioned_throughput = {'ReadCapacityUnits': 30, 'WriteCapacityUnits': 30}

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



def enter_sub_details():
    # Hardcoded email, title, artist, and year
    credentials = [
        {'email': 's39402030@student.rmit.edu.au', 'title': 'Watching the Wheels', 'artist': 'John Lennon', 'year': '1981'},
        {'email': 's39402030@student.rmit.edu.au', 'title': 'Folsom Prison Blues', 'artist': 'Johnny Cash', 'year': '1957'},
        {'email': 's39402030@student.rmit.edu.au', 'title': 'American Girl', 'artist': 'Tom Petty', 'year': '1977'},
        {'email': 's39402031@student.rmit.edu.au', 'title': 'Hey Soul Sister', 'artist': 'Train', 'year': '2009'},
        {'email': 's39402031@student.rmit.edu.au', 'title': 'Darkness Between the Fireflies', 'artist': 'Mason Jennings', 'year': '1997'},
        {'email': 's39402031@student.rmit.edu.au', 'title': 'The Mother We Share', 'artist': 'Chvrches', 'year': '2013'},
        {'email': 's39402032@student.rmit.edu.au', 'title': 'Watching the Wheels', 'artist': 'John Lennon', 'year': '1981'},
        {'email': 's39402032@student.rmit.edu.au', 'title': 'Folsom Prison Blues', 'artist': 'Johnny Cash', 'year': '1957'},
        {'email': 's39402032@student.rmit.edu.au', 'title': 'American Girl', 'artist': 'Tom Petty', 'year': '1977'},
        {'email': 's39402033@student.rmit.edu.au', 'title': 'Hey Soul Sister', 'artist': 'Train', 'year': '2009'},
        {'email': 's39402033@student.rmit.edu.au', 'title': 'Darkness Between the Fireflies', 'artist': 'Mason Jennings', 'year': '1997'},
        {'email': 's39402033@student.rmit.edu.au', 'title': 'The Mother We Share', 'artist': 'Chvrches', 'year': '2013'},
        {'email': 's39402034@student.rmit.edu.au', 'title': 'Watching the Wheels', 'artist': 'John Lennon', 'year': '1981'},
        {'email': 's39402034@student.rmit.edu.au', 'title': 'Folsom Prison Blues', 'artist': 'Johnny Cash', 'year': '1957'},
        {'email': 's39402034@student.rmit.edu.au', 'title': 'American Girl', 'artist': 'Tom Petty', 'year': '1977'},
        {'email': 's39402035@student.rmit.edu.au', 'title': 'Hey Soul Sister', 'artist': 'Train', 'year': '2009'},
        {'email': 's39402035@student.rmit.edu.au', 'title': 'Darkness Between the Fireflies', 'artist': 'Mason Jennings', 'year': '1997'},
        {'email': 's39402035@student.rmit.edu.au', 'title': 'The Mother We Share', 'artist': 'Chvrches', 'year': '2013'},
        {'email': 's39402036@student.rmit.edu.au', 'title': 'Watching the Wheels', 'artist': 'John Lennon', 'year': '1981'},
        {'email': 's39402036@student.rmit.edu.au', 'title': 'Folsom Prison Blues', 'artist': 'Johnny Cash', 'year': '1957'},
        {'email': 's39402036@student.rmit.edu.au', 'title': 'American Girl', 'artist': 'Tom Petty', 'year': '1977'},
        {'email': 's39402037@student.rmit.edu.au', 'title': 'Hey Soul Sister', 'artist': 'Train', 'year': '2009'},
        {'email': 's39402037@student.rmit.edu.au', 'title': 'Darkness Between the Fireflies', 'artist': 'Mason Jennings', 'year': '1997'},
        {'email': 's39402037@student.rmit.edu.au', 'title': 'The Mother We Share', 'artist': 'Chvrches', 'year': '2013'},
        {'email': 's39402038@student.rmit.edu.au', 'title': 'Watching the Wheels', 'artist': 'John Lennon', 'year': '1981'},
        {'email': 's39402038@student.rmit.edu.au', 'title': 'Folsom Prison Blues', 'artist': 'Johnny Cash', 'year': '1957'},
        {'email': 's39402038@student.rmit.edu.au', 'title': 'American Girl', 'artist': 'Tom Petty', 'year': '1977'},
        {'email': 's39402039@student.rmit.edu.au', 'title': 'Hey Soul Sister', 'artist': 'Train', 'year': '2009'},
        {'email': 's39402039@student.rmit.edu.au', 'title': 'Darkness Between the Fireflies', 'artist': 'Mason Jennings', 'year': '1997'},
        {'email': 's39402039@student.rmit.edu.au', 'title': 'The Mother We Share', 'artist': 'Chvrches', 'year': '2013'},
    ]

    # Put each item into the subscription table with a generated subid
    for credential in credentials:
        subid = str(uuid.uuid4())  # Generate a unique subid
        dynamodb.put_item(
            TableName='subscription',
            Item={
                'subid': {'S': subid},  # Store subid as a string
                'email': {'S': credential['email']},
                'title': {'S': credential['title']},
                'artist': {'S': credential['artist']},
                'year': {'N': str(credential['year'])}  # Convert year to string
            }
        )


if __name__ == '__main__':
    # Create subscription table
    sub_table = create_subscription_table()
    print("Subscription table created:", sub_table)

    # Enter subscription details into the subscription table
    enter_sub_details()
    print("Subscription details entered into the subscription table.")
