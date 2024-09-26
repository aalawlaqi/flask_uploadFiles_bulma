import os
from datetime import datetime
from flask import (
    Flask,
    flash,
    request,
    redirect,
    render_template,
    send_from_directory,
    url_for,
    jsonify
)
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'uploads',
)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Add this line for flash messages
app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        # If everything is correct, save the file
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            flash('File successfully uploaded')
            return redirect(url_for('list_files'))

    return render_template('file-upload-template-bulma.html')


@app.route('/list')
def list_files():
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(file_path):
            files.append({
                'name': filename,
                'size': os.path.getsize(file_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            })
    return render_template('file-list-template-bulma.html', files=files)


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/delete/<name>', methods=['POST'])
def delete_file(name):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], name)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'File {name} has been deleted.')
    else:
        flash(f'File {name} not found.')
    return redirect(url_for('list_files'))


if __name__ == '__main__':
    app.run(debug=True)
