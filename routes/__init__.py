from routes.vehicleDbcRoute import vehicleDbcRouter
from routes.dbcRoute import dbcRouter
from routes.vehicleLogsRoute import vehicleLogsRouter

ROUTES = [
    vehicleDbcRouter,
    dbcRouter,
    vehicleLogsRouter, 
]