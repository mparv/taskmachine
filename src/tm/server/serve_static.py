from flask import send_from_directory, render_template

base_url = "https://127.0.0.1:5000"

def serve_public_pages(app):    
    @app.route('/')
    def index():
        return render_template('test_tasks.html', BASE_URL=base_url)

    @app.route('/public/custom-css.css')
    def public_custom_css():
        return send_from_directory('public', 'custom-css.css')

    @app.route("/tokens")
    def tokens_file():
        return render_template('tokens.html', BASE_URL=base_url)

    @app.route('/webapp')
    def webapp():
        return send_from_directory('public', 'webapp.html')

    @app.route('/notes/v1')
    def notes_v1():
        return render_template('notes.html', BASE_URL=base_url)

    @app.route('/admin')
    def admin_v1():
        return render_template("admin.html", BASE_URL=base_url)

    @app.route('/utils/v1/nwusage')
    def nwusage():
        return render_template('nwusage.html', BASE_URL=base_url)

    @app.route('/utils/v1/storage-admin')
    def storage_admin():
        return send_from_directory('public', 'storage_admin.html')

    @app.route('/system')
    def platform():
        return render_template('system.html', BASE_URL=base_url)

    @app.route('/videoapp')
    def videoapp():
        return render_template('nice.html', BASE_URL=base_url)

    @app.route('/investments')
    def investments():
        return render_template('investments.html', BASE_URL=base_url)

    @app.route('/icon')
    def icon():
        return send_from_directory('public', 'icon16.png')

    @app.route("/babel_6.26.0.min.js")
    def babel():
        return send_from_directory('public/external', 'babel_6.26.0.min.js')
    
    @app.route("/bootstrap._4.5.2.min.css")
    def bootstrap():
        return send_from_directory('public/external', 'bootstrap._4.5.2.min.css')
    
    @app.route("/react_17.0.2.development.js")
    def react_development():
        return send_from_directory('public/external', 'react_17.0.2.development.js')

    @app.route('/react-dom_17.0.2.development.js')
    def react_dom():
        return send_from_directory('public/external', 'react-dom_17.0.2.development.js')

    @app.route("/material-ui.production_4.11.0.min.js")
    def material():
        return send_from_directory('public/external', 'material-ui.production_4.11.0.min.js')