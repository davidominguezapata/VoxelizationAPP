from config import config


# API
###########################################################################

# OK
SUCCESSFULL_001 = {'code': 1, 'message': '¡Proceso terminado correctamente!'}

# API ERRORS PARAMETERS
INVALID_RESOLUTION_RANGE_ERROR_010 = {
    'code': 10, 'message': 'La resolución debe ser un valor entero comprendido entre 1 y 8[ambos inclusive].'}
INVALID_RESOLUTION_TYPE_ERROR_011 = {
    'code': 11, 'message': 'La resolución debe ser un nº entero.'}
NOT_ALLOWED_FILE_EXTENSION_ERROR_012 = {
    'code': 12, 'message': 'El archivo debe ser alguna de las siguientes extensiones: {}.'}
MISSING_PARAMETERS_ERROR_013 = {'code': 13,
                                'message': 'Falta algún parámetro: {}'}
INVALID_REMOVE_DISCONNECTED_ELEMENTS_TYPE_ERROR_014 = {
    'code': 14, 'message': 'remove_disconnected_elements debe ser un valor booleano: "true" o "false".'}

# API ERROR with OBJ file
NO_SINGLE_ELEMENT_IN_FILE_ERROR_030 = {
    'code': 30, 'message': 'En el archvio debe existir únicamente 1 elemento/objeto.'}

###########################################################################
