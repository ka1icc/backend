"""API and web routes for the application."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import BASE_DIR, XML_DIR
from app.database import get_db
from app.models import XmlResponse
from app.parser import parse_xml_file
from app.services import compare_routes

router = APIRouter()

templates = Jinja2Templates(
    directory=str(BASE_DIR / 'templates'),
)

_FILE_1 = 'RS_Via-3.xml'
_FILE_2 = 'RS_ViaOW.xml'


@router.post('/load')
def load_data(
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """Parse XML files, store in DB, redirect to main page."""
    for resp in db.query(XmlResponse).all():
        db.delete(resp)
    db.commit()

    parse_xml_file(XML_DIR / _FILE_1, db)
    parse_xml_file(XML_DIR / _FILE_2, db)

    return RedirectResponse(url='/', status_code=303)


@router.get('/api/compare')
def api_compare(
    db: Session = Depends(get_db),
) -> dict:
    """Return route comparison results as JSON."""
    responses = (
        db.query(XmlResponse)
        .order_by(XmlResponse.id)
        .all()
    )
    if len(responses) < 2:
        return {
            'error': 'Data not loaded. POST /load first.',
        }

    return compare_routes(
        list(responses[0].routes),
        list(responses[1].routes),
    )


@router.get('/', response_class=HTMLResponse)
def index(
    request: Request,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Render the main comparison page."""
    responses = (
        db.query(XmlResponse)
        .order_by(XmlResponse.id)
        .all()
    )

    comparison = None
    data_loaded = len(responses) >= 2
    if data_loaded:
        comparison = compare_routes(
            list(responses[0].routes),
            list(responses[1].routes),
        )

    return templates.TemplateResponse(
        'index.html',
        {
            'request': request,
            'comparison': comparison,
            'loaded': data_loaded,
        },
    )
