import uuid

from flask import Flask, render_template, request, redirect, url_for, session
import boto3
from boto3.dynamodb.conditions import Key, Attr

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3')

# Define DynamoDB tables
login_table = dynamodb.Table('login')
sub_table = dynamodb.Table('subscription')
music_table = dynamodb.Table('music')


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # Check if user credentials are valid
    if validate_credentials(email, password):
        # Set session variable to indicate user is logged in
        session['email'] = email
        # Redirect to main page if credentials are valid
        return redirect(url_for('main_page'))
    else:
        # Display error message and stay on the login page
        error = 'Email or password is invalid'
        return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        user_name = request.form['user_name']
        password = request.form['password']

        # Check if the entered email already exists in the login table
        if email_exists(email):
            error = 'The email already exists'
            return render_template('register.html', error=error)
        else:
            # If email is unique, store the new user information in the login table
            add_user(email, user_name, password)
            return redirect(url_for('index'))  # Redirect to login page after successful registration

    return render_template('register.html')


# Helper function to retrieve the username associated with the email from DynamoDB
def get_user_name(email):
    try:
        response = login_table.get_item(
            Key={
                'email': email
            },
            ProjectionExpression='user_name'  # Assuming the attribute name is 'username'
        )

        if 'Item' in response:
            return response['Item']['user_name']  # Assuming the attribute type is 'S'
        else:
            return None  # Return None if user not found
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        # Handle case where login table does not exist
        return None


def validate_credentials(email, password):
    # Check if the provided email and password match any entry in the login table
    try:
        response = login_table.get_item(
            Key={
                'email': email
            },
            ProjectionExpression='password'
        )

        # If response contains 'Item' and password matches, credentials are valid
        if 'Item' in response and response['Item']['password'] == password:
            return True
        else:
            return False
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        # Handle case where login table does not exist
        return False


def email_exists(email):
    # Check if the provided email already exists in the login table
    try:
        response = login_table.get_item(
            Key={
                'email': email
            }
        )

        # If response contains 'Item', email exists in the table
        if 'Item' in response:
            return True
        else:
            return False
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        # Handle case where login table does not exist
        return False


def add_user(email, user_name, password):
    # Add a new user to the login table
    try:
        login_table.put_item(
            Item={
                'email': email,
                'user_name': user_name,
                'password': password
            }
        )
    except Exception as e:
        # Handle any errors that occur during user registration
        print(f"Error adding user: {e}")


@app.route('/main')
def main_page():
    if 'email' in session:
        email = session['email']
        user_name = get_user_name(email)

        # Fetch subscribed music information from DynamoDB subscription table using email
        subscribed_music = get_subscribed_music(email)

        # Check if there is a query request
        queried_items = None
        if 'queried_items' in session:
            queried_items = session['queried_items']
            # Clear the queried items session data
            session.pop('queried_items', None)

        # Update subscribed music with artist image URLs
        for music in subscribed_music:
            artist = music['artist']
            music['artist_image_url'] = get_artist_image(artist)

        if request.method == 'POST':
            # Handle subscription request
            result = subscribe_music()
            if result == 'Music subscribed successfully':
                # If music is subscribed successfully, fetch updated subscribed music information
                subscribed_music = get_subscribed_music(email)
                # Update subscribed music with artist image URLs
                for music in subscribed_music:
                    artist = music['artist']
                    music['artist_image_url'] = get_artist_image(artist)

        return render_template('main.html', user_name=user_name,
                               subscribed_music=subscribed_music,
                               queried_items=queried_items)
    else:
        return redirect(url_for('index'))


def get_subscribed_music(email):
    try:
        response = sub_table.scan(
            FilterExpression=Attr('email').eq(email)
        )

        subscribed_music = []
        for item in response['Items']:
            subscribed_music.append({
                'subid': item['subid'],
                'email': item['email'],
                'title': item['title'],
                'artist': item['artist'],
                'year': item['year']
            })

        return subscribed_music
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        return []


def get_artist_image(artist):
    # Convert artist name to the format used in S3 bucket (remove spaces and add .jpg suffix)
    image_key = artist.replace(' ', '') + '.jpg'

    try:
        # Get the object (image) from the S3 bucket
        s3.get_object(
            Bucket='mymusicbckt',
            Key=image_key
        )

        # # Read the image data from the response
        # image_data = response['Body'].read()

        # Generate a pre-signed URL for the image
        image_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': 'mymusicbckt', 'Key': image_key},
            ExpiresIn=3600  # URL expires in 1 hour (adjust as needed)
        )

        return image_url
    except Exception as e:
        # Handle any errors that occur during image retrieval
        print(f"Error fetching image: {e}")
        return None


@app.route('/query_music', methods=['GET', 'POST'])
def query_music():
    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')
        artist = request.form.get('artist')

        if title and year and artist:  # Check if at least one search parameter is provided
            response = music_table.query(
                KeyConditionExpression=Key('title').eq(title) & Key('artist').eq(artist),
                FilterExpression=Attr('year').eq(year)
            )
        elif title:
            response = music_table.query(KeyConditionExpression=Key('title').eq(title))
        elif year:
            response = music_table.scan(FilterExpression=Attr('year').eq(year))
        elif artist:
            response = music_table.scan(FilterExpression=Attr('artist').eq(artist))
        elif title and year:
            response = music_table.query(
                KeyConditionExpression=Key('title').eq(title),
                FilterExpression=Attr('year').eq(year)
            )
        elif title and artist:
            response = music_table.query(KeyConditionExpression=Key('title').eq(title) & Key('artist').eq(artist))
        elif year and artist:
            response = music_table.scan(FilterExpression=Attr('year').eq(year) & Attr('artist').eq(artist))
        else:
            response = music_table.scan()

        items = response['Items']

        # Store queried items in session
        session['queried_items'] = items
        # get the url of the image from s3

        # if items list is empty, return a message
        if not items:
            msg1 = "No result is retrieved. Please query again!"
            return render_template('main.html', msg1=msg1)

        s3 = boto3.client('s3')
        for item in items:
            temp_artist = item['artist'].replace(' ', '')

            key = f"{temp_artist}.jpg"

            url = s3.generate_presigned_url('get_object', Params={'Bucket': 'mymusicbckt', 'Key': key})
            item['url'] = url

        return redirect(url_for('main_page'))  # Redirect to main page to display the results
    else:
        return render_template('main.html')  # Render default template


@app.route('/subscribe_music', methods=['POST'])
def subscribe_music():
    if 'email' in session:
        email = session['email']
        title = request.form.get('title')

        # Check if the music is already subscribed
        if is_music_subscribed(email, title):
            # Music is already subscribed, return message
            return 'Music already subscribed'
        else:  # If not subscribed, proceed with subscription
            artist = request.form.get('artist')
            year = request.form.get('year')

            try:
                # Generate a unique subscription ID
                subid = str(uuid.uuid4())

                # Add the subscribed music information to the subscription table
                sub_table.put_item(
                    Item={
                        'subid': subid,
                        'email': email,
                        'title': title,
                        'artist': artist,
                        'year': year  # No need to convert year to string here
                    }
                )

                # Fetch updated subscribed music information
                subscribed_music = get_subscribed_music(email)

                # Update subscribed music with artist image URLs
                for music in subscribed_music:
                    artist = music['artist']
                    music['artist_image_url'] = get_artist_image(artist)

                # Render the main.html template with updated subscribed music
                user_name = get_user_name(email)  # Retrieve user_name for rendering
                return render_template('main.html', user_name=user_name, subscribed_music=subscribed_music)
            except Exception as e:
                print(f"Error subscribing music: {e}")
                return 'An error occurred while subscribing to music'
    else:
        return 'User not logged in'


def is_music_subscribed(email, title):
    try:
        response = sub_table.scan(
            FilterExpression=Attr('email').eq(email) & Attr('title').eq(title)
        )
        items = response['Items']
        # Check if both email and title exist in the same row
        return len(items) > 0 and all(item['email'] == email and item['title'] == title for item in items)
    except Exception as e:
        print(f"Error checking if music is subscribed: {e}")
        return False


@app.route('/remove_music', methods=['POST'])
def remove_music():
    if 'email' in session:
        subid = request.form.get('subid')  # Get the subscription ID
        print(subid)
        email = session['email']  # Get the user's email from session

        try:
            # Delete the subscribed music entry from the subscription table
            sub_table.delete_item(
                Key={
                    'subid': subid,
                    'email': email
                }
            )

            # Fetch updated subscribed music information after removal
            subscribed_music = get_subscribed_music(email)

            # Update subscribed music with artist image URLs
            for music in subscribed_music:
                artist = music['artist']
                music['artist_image_url'] = get_artist_image(artist)

            # Render the main.html template with updated subscribed music
            user_name = get_user_name(email)  # Retrieve user_name for rendering
            return render_template('main.html', user_name=user_name, subscribed_music=subscribed_music)
        except Exception as e:
            print(f"Error removing music: {e}")
            return 'An error occurred while removing the music'
    else:
        return 'User not logged in'


@app.route('/logout')
def logout():
    session.pop('email', None)  # Remove email from session
    return redirect(url_for('index'))  # Redirect to login page


if __name__ == '__main__':
    app.run(debug=True)
