import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify,  make_response
from cloudant.client import Cloudant
import json
import hashlib
import datetime
import shutil

app = Flask(__name__)

credential = {
  "username": "YOUR USERNAME",
  "password": "YOUR PASSWORD",
  "host": "YOUR HOST URI",
  "port": 443,
  "url": "YOUR URL"
}
# BLOCKSIZE = 65536
DB_NAME = 'cc_6331'

def connect_cloudant() :
    client = Cloudant(credential['username'], credential['password'], url=credential['url'])
    client.connect()
    return client

def connect_db() :
    client = connect_cloudant()
    connected_db_instance = client[DB_NAME]
    return connected_db_instance

@app.route('/upload', methods=['POST'])
def upload_file() :
    uploaded_files = {}
    file_from_page = request.files.getlist('file')
    files = []
    for it in file_from_page :
        files.append(it)
    cloudant_db_instance = connect_db()

    for document in cloudant_db_instance :
        if (document["filename"] in uploaded_files):
            temp_list = []
            temp_list = uploaded_files[document["filename"]]
            temp_list.append(document["hashed_value"])
            uploaded_files[document["filename"]] = temp_list
        else :
            uploaded_files[document["filename"]]= [document["hashed_value"]]
    already_exist_file= []
    for file_it in files:
        hasher = hashlib.md5()
        if uploaded_files :
            if (file_it.filename in uploaded_files):
                buf = file_it.read()
                hasher.update(buf)
                if (hasher.hexdigest() in uploaded_files[file_it.filename]):
                    print "If file hash is same and exist...."
                    already_exist_file.append(file_it.filename)
                    print ', '.join(already_exist_file)
                else :
                    print "If file hash not same exist...."
                    data = {
                                'filename':file_it.filename,
                                'hashed_value': hasher.hexdigest(),
                                'version_number': len(uploaded_files[file_it.filename]) + 1,
                                'last_modified_date': datetime.datetime.now().__str__(),
                                'content_file': buf
                            }
                    cloudant_db_instance.create_document(data)
            else:
                print "This is if to check uploaded_files not null and file name not in it.."
                buf = file_it.read()
                hasher.update(buf)
                data = {
                            'filename':file_it.filename,
                            'hashed_value': hasher.hexdigest(),
                            'version_number': 1,
                            'last_modified_date': datetime.datetime.now().__str__(),
                            'content_file': buf
                        }
                cloudant_db_instance.create_document(data)
        else :
            buf = file_it.read()
            hasher.update(buf)
            data = {
                    'filename':file_it.filename,
                    'hashed_value': hasher.hexdigest(),
                    'version_number': 1,
                    'last_modified_date': datetime.datetime.now().__str__(),
                    'content_file': buf,
                    '_attachments': {file_name : {'data': buf}}
                }
            cloudant_db_instance.create_document(data)
    if already_exist_file :
        return ', '.join(already_exist_file)
    else :
        return redirect('/')

@app.route('/', methods=['POST'])
def download_delete_file() :
    request_from_page = request.form
    print request_from_page
    filename = [it for it in request_from_page][0]
    print "This is the filename in downloaddelte %s"%filename
    version = filename.split('~~')[2]
    function_to_perform = filename.split('~~')[1]
    filename = filename.split('~~')[0]

    cloudant_db_instance = connect_db()

    for document in cloudant_db_instance :
        if (document['filename'] == filename and document['version_number'] == int(version)) :
            if (function_to_perform == 'Download') :
                file_content = document['content_file']
                response = make_response(file_content)
                response.headers["Content-Disposition"] = "attachment; filename="+document['filename']
                response.headers["Cache-Control"] = "must-revalidate"
                response.headers["Pragma"] = "must-revalidate"
                response.headers["Content_type"] = "application/"+document['filename'].split('.')[1]
                print "response =======>>>>> %s"%response
                return response
            elif(function_to_perform == 'Delete') :
                print "This is delete ......."
                document.delete()
                return redirect('/')

@app.route('/')
def index():
    cloudant_db_instance = connect_db()
    uploaded_files = []
    path = "YOUR LOCAL MACHINE PATH"
    dirsa = os.listdir( path )
    listed_nontext_file = []

    for file in dirsa :
        listed_nontext_file.append(file)

    for document in cloudant_db_instance:
        uploaded_files.append(document)
    return render_template('index.html', uploaded_files=uploaded_files, listed_nontext_file = listed_nontext_file)

if __name__ == "__main__":
	app.run(debug=True)
