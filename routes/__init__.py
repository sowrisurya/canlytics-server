from routes.vehicleDbcRoute import vehicleDbcRouter
from routes.dbcRoute import dbcRouter
from routes.vehicleLogsRoute import vehicleLogsRouter
from routes.vehicleRoute import vehicleRouter

ROUTES = [
    vehicleDbcRouter,
    dbcRouter,
    vehicleLogsRouter, 
    vehicleRouter, 
]