from flask import Flask, render_template, send_file, Response
from docx import Document
from io import BytesIO
from core import generate_motion_using_file
from werkzeug.wsgi import FileWrapper

app = Flask(__name__)

@app.route('/')
def index():
    return "Index"
"""
@app.route('/motion-test/<docket_number>')
def motion_test(docket_number):
    title, document = generate_motion_using_file(docket_number)
    f = BytesIO()
    document.save(f)
    length = f.tell()
    f.seek(0)
    return send_file(f, as_attachment=True, attachment_filename=title)
"""
@app.route('/motion/<docket_number>')
def motion(docket_number):
    title, document = generate_motion_using_file(docket_number)
    f = BytesIO()
    document.save(f)
    f.seek(0)
    return Response(FileWrapper(f),
                    mimetype="text/docx",
                    direct_passthrough=True,
                    headers = {
                        'Content-Disposition': 'attachment; filename="{}.docx"'.format(title)
                    })

if __name__ == '__main__':
    app.run()