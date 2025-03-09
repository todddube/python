import logging
import azure.functions as func
import requests
import json


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Function invoked..')
    queryparm_key_name = "default"
    key_value = "9RYzZt6YIanerzKqTy75P1APhhBM7t7rXLYFfNr2pV7am092QNMiJw=="
    endpoint_name='com.carmax.customer.progression.updated.v1'
    messaging_api_url="https://messaging-dev.services.carmax.com/"

    
    response = {}

    def validation_responder(req):
        validation_response = {}
        logging.info("Performing API Key validation...")
 
        if req.params.get('apiKey') == key_value:
            logging.info("API Key matched...")
            headers = {'WebHook-Allowed-Origin':'*','WebHook-Allowed-Rate':'*'}
            validation_response['headers'] = headers
            validation_response['status'] = True
            validation_response['body'] = "API Key validation SUCCESS"
        else:
            logging.info("API Key NOT matched...")
            validation_response['body'] = "API Key validation failed"
            validation_response['status'] = False
        
        return validation_response
        
    def handle_event(req):

        log_msg = ''
        log_msg = log_msg + 'Handling event : '
        # logging.info("Received Progression event...")
        # logging.info("Request Body : " + str(req.get_body()))
        req_body = req.get_json()
        data = req_body['data']
        identities = data['identities']
        for each_identity in identities:
            log_msg = log_msg + each_identity['type'] + ':' + each_identity['value']
        log_msg = log_msg + " Update Reason : " + data['updateReason']
        
        logging.info(log_msg)
      
       
    try:
        print("Request Body : " + str(req.get_body()), len(req.get_body()))
        response = validation_responder(req)  
        if response['status'] :  
            if   len(req.get_body()) == 0 or None:         
                return func.HttpResponse(response['body'],status_code=200, headers=response['headers'] )
            else:
                handle_event(req)   
                return func.HttpResponse("Handled event..",status_code=200 )        
        else:
            return func.HttpResponse(response['body'],status_code=401)
        
    except Exception as e:
        print("from exception", str(e))
        logging.info("logging exception")
        logging.info(str(e))
        return func.HttpResponse("Exception occured :" + str(e),status_code=200 )

