import os
from werkzeug import secure_filename
from flask import Flask, render_template, request, g , jsonify
from flask import send_from_directory, redirect, url_for
import models.fast_transfer as fast_transfer
import models.style_swap_transfer as style_swap_transfer
import models.mask_style_transfer as mask_style_transfer
import multiprocessing as mp
import base64, json, sys
import style_names
import gc


## Declare allowed file extensions
ALLOWED_EXTENSIONS = set(['png', 'jpg','jpeg' ,'gif', 'bmp', 'jpe', 'gif', 'svg'])

## Initialize flask app.
app = Flask(__name__)

lock = mp.Lock()

## This function check whether the file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


## Render Index Page
@app.route('/')
def index():
    return render_template(
        'index.html')

@app.route('/faststyle')
def fastStyle():
    return render_template(
        'fastStyle.html')

@app.route('/maskstyle')
def maskStyle():
    return render_template(
        'maskStyle.html')

@app.route('/styleswap')
def styleSwap():
    return render_template(
        'styleSwap.html')

@app.route('/about')
def about():
    return render_template(
        'about.html')

## Deal with upload request
@app.route('/upload_image', methods=['POST'])
def upload_file():
    ## Get message from the form
    file = request.files['file']
    style = request.form['style']
    ## Print style to log
    print(style, file=sys.stdout)
    style_image_path = None
    ## Check style
    style_image_path = style_names.get_style_path(style)
    
    if not style_image_path:
        json_data = json.dumps({'error':'No style image found'})
        return json_data
    
    ## If file is valid
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        ## Start transfer
        #data = transfer.transfer(file, STYLE_IMG_PATH)
        lock.acquire()
        data = fast_transfer.transfer(file, style_image_path)
        lock.release()
        ## encode image data to base64
        data = base64.b64encode(data).decode('UTF-8')
        ## put data into json
        gc.collect()
        json_data = json.dumps({'image':data})
        return json_data

## Deal with upload request
@app.route('/styleswap_upload_image', methods=['POST'])
def styleswap_upload_file():
    ## Get message from the form
    file = request.files['file']
    style = request.files['style']

    
    ## If file is valid
    if file and allowed_file(file.filename):
        if style and allowed_file(style.filename):
            filename = secure_filename(file.filename)

            ## Start transfer
            lock.acquire()
            data = style_swap_transfer.transfer(file, style)
            lock.release()
            ## encode image data to base64
            data = base64.b64encode(data).decode('UTF-8')
            ## put data into json
            gc.collect()
            json_data = json.dumps({'image':data})
            return json_data
        else:
            json_data = json.dumps({'error':'Style image format not supported'})
            return json_data
    else:
        json_data = json.dumps({'error':'Content image format not supported'})
        return json_data

## Deal with upload request
@app.route('/maskstyle_upload_image', methods=['POST'])
def maskstyle_upload_file():
    ## Get message from the form
    file = request.files['file']
    forestyle = request.form['forestyle']
    backstyle = request.form['backstyle']

    forestyle_image_path = None
    backstyle_image_path = None
    ## Check style
    forestyle_image_path = style_names.get_style_path(forestyle)
    backstyle_image_path = style_names.get_style_path(backstyle)
    
    if not forestyle_image_path or not backstyle_image_path:
        json_data = json.dumps({'error':'No style image found'})
        return json_data

    ## If file is valid
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        ## Start transfer
        lock.acquire()
        data = mask_style_transfer.transfer(file, forestyle_image_path, backstyle_image_path)
        lock.release()
        ## encode image data to base64
        data = base64.b64encode(data).decode('UTF-8')
        ## put data into json
        gc.collect()
        json_data = json.dumps({'image':data})
        return json_data
    else:
        json_data = json.dumps({'error':'Content image format not supported'})
        return json_data

@app.route('/dropzone_dummy', methods=['GET'])
def dropzone_dummy():
    ## For dropzone
    return ''

if __name__ == '__main__':
    app.run(debug=True)
