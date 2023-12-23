from flask import Flask, request, jsonify
from flask_cors import cross_origin
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
# Path to the directory containing the text files
text_files_directory = 'uploads/'


def check_words_in_files(typed_words):
    found_words = set()

    # Iterate over each text file
    for filename in os.listdir(text_files_directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(text_files_directory, filename)

            # Read the content of the text file
            with open(file_path, 'r') as file:
                file_content = file.read()

                # Check if each typed word is present in the file
                for word in typed_words:
                    if word.lower() in file_content.lower():
                        found_words.add(word)

    return found_words


@app.route('/get_typed_words', methods=['POST'])
@cross_origin()
def get_typed_words():
    try:
        data = request.get_json()
        typed_words = data.get('words', [])

        # Process the list of typed words as needed
        found_words = check_words_in_files(typed_words)

        response_message = f"Found words: {', '.join(found_words)}" if found_words else "No matching words found"

        return jsonify({'success': True, 'message': response_message, 'found_words': list(found_words)})
    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False, 'message': 'Error processing typed words'})


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Update the route to handle a single file
@app.route('/upload_file', methods=['POST'])
@cross_origin()
def upload_file():
    try:
        # Check if file is present in the request
        if 'textFile' not in request.files:
            return jsonify({'message': 'No file part'}), 400

        file = request.files['textFile']

        # Check if the file has a filename
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400

        # Save the file to the uploads directory
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        return jsonify({'message': 'File uploaded successfully'})

    except Exception as e:
        print(str(e))
        return jsonify({'message': 'Error uploading file'}), 500


if __name__ == '__main__':
    app.run(debug=True)
