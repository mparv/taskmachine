from flask import request

def create_line_db_routes(app, file_client):
        
    def validate_universe_input(request):
        token = request.headers.get("Bearer-Token", "")
        if token != "16-Nov-24":
            return False
    
        inp = request.get_json()
        if not inp.get("tenant") or not inp.get("database") or not inp.get("table"):
            return False
        
        if not inp.get("dataObject"):
            return False
        
        return True
        
    def validate_universe_input_non_data(request):
        token = request.headers.get("Bearer-Token", "")
        if token != "16-Nov-24":
            return False
    
        inp = request.get_json()
        if not inp.get("tenant") or not inp.get("database") or not inp.get("table"):
            return False
        
        return True

    @app.route('/internal/universe/create', methods=['POST'])
    def universe_create():
        if not validate_universe_input(request):
            return "Invalid request", 404
        
        inp = request.get_json()
        file_client.append_data(
            inp.get("tenant"),
            inp.get("database"),
            inp.get("table"),
            inp.get('dataObject')
        )
        return "", 200
        
    @app.route("/internal/universe/read", methods=['POST'])
    def universe_read():
        if not validate_universe_input_non_data(request):
            return "Invalid request", 404
        
        inp = request.get_json()
        resp = file_client.read_data(
            inp.get("tenant"),
            inp.get("database"),
            inp.get("table")
        )

        resp_serial = [x.fields for x in resp]
        return resp_serial, 200

    @app.route("/internal/universe/delete", methods=['POST'])
    def universe_delete():
        if not validate_universe_input_non_data(request):
            return "Invalid request", 404
        
        inp = request.get_json()
        file_client.delete_data(
            inp.get("tenant"),
            inp.get("database"),
            inp.get("table")
        )

        return "", 200