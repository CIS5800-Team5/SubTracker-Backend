import logging
import json

import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    products = [
        {
            "name": "Azure DevOps",
            "price": 4.99
        },
        {
            "name": "Azure Functions",
            "price": 0.01
        }
    ]

    return func.HttpResponse(json.dumps(products))
