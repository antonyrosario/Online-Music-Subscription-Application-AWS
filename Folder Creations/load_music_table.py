import json
import boto3

def load_table(music_list):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    # Get the DynamoDB table
    table = dynamodb.Table('music')

    # Insert each song individually into the DynamoDB table
    for song in music_list:
        title = song['title']
        artist = song['artist']
        print("Music added:", title, artist)
        table.put_item(Item=song)

if __name__ == '__main__':
    # Read data from JSON file
    with open('a1.json') as file:
        music_list = json.load(file)

    # Load music data into DynamoDB
    load_table(music_list['songs'])

    print("Music data loaded into DynamoDB.")
