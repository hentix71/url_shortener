from rest_framework import status   
from rest_framework.response import Response

def api_response(
    result : str = None,
    is_success: bool = True,
    message : str = "Success", 
    status_code=status.HTTP_200_OK
) -> Response:
    # building the standard response format for all the API responses

    return Response(
    {
        "is_success": is_success,
        "message": message,
        "result": result,
    },
    status=status_code
)