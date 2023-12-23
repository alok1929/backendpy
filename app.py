from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import os
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'docx'}


def extract_text_from_docx(docx_file_path):
    doc = Document(docx_file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + " "
    return text.lower()


def compare_similarity_with_keywords(docx_folder_path, uploaded_docx_path, keywords):
    # Extract text from the uploaded document
    uploaded_text = extract_text_from_docx(uploaded_docx_path)

    doc_texts = [extract_text_from_docx(os.path.join(docx_folder_path, filename))
                 for filename in os.listdir(docx_folder_path) if filename.endswith(".docx")]
    doc_texts.append(uploaded_text)

    # Create a TfidfVectorizer with specified keywords
    vectorizer = TfidfVectorizer(vocabulary=keywords, stop_words='english')

    # Transform the documents into TF-IDF vectors
    tfidf_matrix = vectorizer.fit_transform(doc_texts)

    # Calculate cosine similarity between the documents
    similarities = cosine_similarity(tfidf_matrix)

    docx_files = []

    for i, filename in enumerate(os.listdir(docx_folder_path)):
        if filename.endswith(".docx"):
            # Similarity with the uploaded document
            similarity = similarities[-1, i]
            docx_files.append(
                {"name": filename, "similarity": similarity * 100})

    return docx_files


@app.route('/upload_file', methods=['POST'])
@cross_origin()
def upload_file():
    try:
        # Check if the 'textFile' key is in the files
        if 'textFile' not in request.files:
            return jsonify({'message': 'No file part'}), 400

        file = request.files['textFile']

        # Check if the file has a filename
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400

        # Check if the file has an allowed extension
        if not allowed_file(file.filename):
            return jsonify({'message': 'Invalid file extension'}), 400

        # Save the file to the uploads directory
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        return jsonify({'message': 'File uploaded successfully'})

    except Exception as e:
        print(str(e))
        return jsonify({'message': 'Error uploading file'}), 500


@app.route('/get_similarity', methods=['POST'])
@cross_origin()
def get_similarity():
    try:
        # Get the uploaded DOCX file path from the request
        uploaded_docx_filename = request.json.get('uploaded_docx_filename')
        uploaded_docx_path = os.path.join(
            app.config['UPLOAD_FOLDER'], uploaded_docx_filename)

        # Get the folder path containing DOCX files
        docx_folder_path = app.config['UPLOAD_FOLDER']

        # Get keywords from the request body
        keywords = request.json.get('keywords', [])

        # Implement the similarity calculation logic
        docx_files = compare_similarity_with_keywords(
            docx_folder_path, uploaded_docx_path, keywords)

        return jsonify({'success': True, 'message': 'Similarities calculated successfully', 'docx_files': docx_files})

    except Exception as e:
        print(str(e))
        return jsonify({'success': False, 'message': 'Error calculating similarities'}), 500



# Run the app if the script is executed directly
if __name__ == "__main__":
    app.run(debug=True)

