from sanic import response
from .main import bp_wzgj


@bp_wzgj.get('/again')
async def test(req):
    return response.text('again')    
