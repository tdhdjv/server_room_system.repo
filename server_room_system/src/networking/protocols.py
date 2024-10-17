class Protocol:
    class Response:
        CLIENT_DATA = 'response.client_data'
        MESSAGE = 'response.message'
        COMMAND = 'response.command'
        
    class Request:
        ROOM_RULSET = 'request.room_ruleset'
        MESSAGE = 'request.message'
        COMMAND = 'request.command'