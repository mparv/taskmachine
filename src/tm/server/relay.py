import requests

def create_investment_routes(app):
      
    @app.route("/investments/v1/stocks_pnl")
    def investments_v1_stocks_pnl():
        return requests.get("http://localhost:6001/internal/v1/investments/stocks/pnl").json()

    @app.route("/investments/v1/stocks_specific")
    def investments_v1_stocks_specific():
        return requests.get("http://localhost:6001/internal/v1/investments/stocks/specific").json()
    
    @app.route("/investments/v1/stocks_sectors")
    def investments_v1_stocks_sectors():
        return requests.get("http://localhost:6001/internal/v1/investments/stocks/sectors").json()

    @app.route("/investments/v1/orders")
    def investments_v1_orders():
        return requests.get("http://localhost:6001/internal/v1/investments/orders").json()