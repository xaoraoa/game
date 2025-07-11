from backend.server import app
from mangum import Mangum

handler = Mangum(app)