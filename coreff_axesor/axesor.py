import xml.etree.ElementTree as ET
import xml.dom.minidom
import hashlib


def get_text_safely(tree, path):
    fetch_val = tree.findall(f"./{path}",{"":"*"})
    if fetch_val:
        return fetch_val[0].text
    else:
        return ""

def search_parse(response:str):
    root = ET.fromstring(response)
    companies = root.findall("./ListaPaquetesNegocio/ListaSociedades/Sociedad",{"":"*"})
    companies_infos = []
    for company in companies:
        company_infos = {}
        company_infos["name"] = get_text_safely(company,"NombreSociedad")
        company_infos["coreff_company_code"] = get_text_safely(company,"Cif")
        company_infos["axesor_internal_id"] = company.get("CodInfotel")
        companies_infos.append(company_infos)
    return companies_infos

def search_by_name(user, password, company_name, session):
    params = {"cod_usuario": user, "accion": "3"}
    params.update({"nombreSociedad": company_name})

    cadena = "".join(params.values())
    digest = hashlib.sha3_256((cadena + password).encode("iso-8859-1")).hexdigest()
    params["crc"] = digest

    with session as s:
        res = s.get("https://www.axesor.es/buscador-unificado", params=params)
    return search_parse(res.text)

def search_by_code(user, password, code, session):
    params = {"cod_usuario": user, "cod_servicio": "388", "cod_idioma": "2"}
    params.update({"cif": code})

    cadena = "".join(params.values())
    digest = hashlib.sha3_256((cadena + password).encode("iso-8859-1")).hexdigest()
    params["crc"] = digest

    with session as s:
        res = s.get("https://informes.axesor.es/informe", params=params)
    return parse_search_code(res.text)

def get_infos(user, password, code, session):
    params = {"cod_usuario": user, "cod_servicio": "388", "cod_idioma": "2"}
    params.update({"cif": code})

    cadena = "".join(params.values())
    digest = hashlib.sha3_256((cadena + password).encode("iso-8859-1")).hexdigest()
    params["crc"] = digest

    with session as s:
        res = s.get("https://informes.axesor.es/informe", params=params)
    return parse_infos(res.text)

def parse_search_code(response:str):
    root = ET.fromstring(response)[0]
    infos = {}
    infos["name"] = get_text_safely(root, "SeccionDatosGenerales/Nombre")
    infos["coreff_company_code"] = get_text_safely(root, "ListaSubvencionesBoletin/Subvencion/Cif")
    infos["axesor_internal_id"] = root.findall("./EstadisticaSociedadSector", {"":"*"})[0].get("CodInfotel")
    return [infos]

def parse_infos(response:str):
    root = ET.fromstring(response)[0]
    infos = {}
    infos["street"] = get_text_safely(root, "ListaDelegaciones/Delegacion/Domicilio")
    infos["city"] = get_text_safely(root, "ListaDelegaciones/Delegacion/Municipio")
    infos["zip"] = get_text_safely(root, "ListaDelegaciones/Delegacion/CodigoPostal")
    infos["state"] = get_text_safely(root, "ListaDelegaciones/Delegacion/Provincia")
    infos["phone"] = get_text_safely(root, "SeccionDatosGenerales/DatosContacto/Telefono")
    infos["email"] = get_text_safely(root, "SeccionDatosGenerales/DatosContacto/Email")
    infos["website"] = get_text_safely(root, "SeccionDatosGenerales/DatosContacto/Url")
    infos["axesor_risk_score"] = get_text_safely(root, "Rating/RatingAxesorDef")
    infos["tax_id"] = get_text_safely(root, "IdentificacionBalance/IdentificacionSociedad/Nif")
    infos["axesor_data"] = xml.dom.minidom.parseString(response).toprettyxml()
    return infos
