import os
from flask import Flask, render_template, request, abort, send_file, redirect, send_from_directory
from werkzeug.utils import secure_filename
from zipfile import ZipFile
import pathlib
import io
#TODO: Remember to check if you can upload files with spaces in it


app = Flask(__name__)
app.config['UPLOAD_PATH'] = 'storage'

def unzipFolder(name):
    with ZipFile(name, 'r') as zipObj:
        zipObj.extractall('storage/' + name[:-4] + '/')
    os.remove(name)

@app.route('/upload')
def index():
    with open('./index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/delete/<path:pathToFile>', methods=['GET'])
def delete(pathToFile):
    os.remove(os.path.join('./storage/' + pathToFile))
    return 'Success', 200

@app.route('/api/download/<path:pathToFile>', methods=['GET'])
def download(pathToFile):
    if os.path.isdir(os.path.join('./storage/' + pathToFile)):
        base_path = pathlib.Path('./storage/' + pathToFile)
        data = io.BytesIO()
        with ZipFile(data, mode='w') as z:
            for f in base_path.iterdir():
                z.write(f)
        data.seek(0)
        return send_file(data, download_name='download.zip', as_attachment=True, mimetype='application/zip')
    return send_file(os.path.join('./storage/' + pathToFile), as_attachment=True)


@app.route('/')
def home():
    return redirect('/view')

@app.route('/icons/<filename>')
def icons(filename):
    return send_file(os.path.abspath('./templates/icons/' + filename))

@app.route('/view', defaults={'req_path': ''})
@app.route('/view/<path:req_path>')
def dir_listing(req_path):
    BASE_DIR = './storage'

    # Joining the base and the requested path
    abs_path = os.path.join(BASE_DIR, req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = next(os.walk(abs_path))[1]
    folders = next(os.walk(abs_path))[2]
    if req_path == '':
        back = False 
    else:
        back = True
    return render_template('files.html', files=files, folders=folders, back=back)

@app.route('/upload', methods=['POST'])
def upload_files():
    uploaded_file = request.files.getlist("file")
    for item in uploaded_file:
        filename = secure_filename(item.filename)
        if filename.endswith('.zip'):
            item.save(filename)
            unzipFolder(filename)
        elif filename != '':
            item.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    with open('./success.html', 'r', encoding='utf-8') as f:
        return f.read()



if __name__ == "__main__":
    app.run()