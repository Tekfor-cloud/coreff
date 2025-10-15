import xml.etree.ElementTree as ET
import xml.dom.minidom
import hashlib


def get_text_safely(tree, path):
    fetch_val = tree.find(f".//{path}", {"": "*"})
    return fetch_val.text if fetch_val is not None else ""


def search_parse(response: str):
    root = ET.fromstring(response)
    companies = root.findall(
        "./ListaPaquetesNegocio/ListaSociedades/Sociedad", {"": "*"}
    )
    companies_infos = []
    for company in companies:
        company_infos = {}
        company_infos["name"] = get_text_safely(company, "NombreSociedad")
        company_infos["coreff_company_code"] = get_text_safely(company, "Cif")
        company_infos["axesor_internal_id"] = company.get("CodInfotel")
        companies_infos.append(company_infos)
    return companies_infos


def search_by_name(user, password, company_name, session):
    params = {"cod_usuario": user, "accion": "3"}
    params.update({"nombreSociedad": company_name})

    cadena = "".join(params.values())
    digest = hashlib.sha3_256(
        (cadena + password).encode("iso-8859-1")
    ).hexdigest()
    params["crc"] = digest

    with session as s:
        res = s.get("https://www.axesor.es/buscador-unificado", params=params)
    return search_parse(res.text)


def search_by_code(user, password, code, session):
    return search_by_name(user, password, code, session)


def get_infos(user, password, code, session):
    params = {
        "cod_usuario": user,
        "cod_servicio": "388",
        "cod_idioma": "2",
        "tip_formato": "2",
    }
    params.update({"cif": code})

    cadena = "".join(params.values())
    digest = hashlib.sha3_256(
        (cadena + password).encode("iso-8859-1")
    ).hexdigest()
    params["crc"] = digest

    with session as s:
        res = s.get("https://informes.axesor.es/informe", params=params)
    return parse_infos(res.text)


def get_infos_pdf(user, password, code, session):
    params = {
        "cod_usuario": user,
        "cod_servicio": "388",
        "cod_idioma": "2",
        "tip_formato": "3",
    }
    params.update({"cif": code})

    cadena = "".join(params.values())
    digest = hashlib.sha3_256(
        (cadena + password).encode("iso-8859-1")
    ).hexdigest()
    params["crc"] = digest

    with session as s:
        res = s.get("https://informes.axesor.es/informe", params=params)
    return res.content


def parse_infos(response: str):
    root = ET.fromstring(response)
    infos = {}
    infos["internal_id"] = root.find(
        ".//EstadisticaSociedadSector", {"": "*"}
    ).get("CodInfotel")
    infos["street"] = get_text_safely(root, "DatosContacto/Domicilio")
    infos["city"] = get_text_safely(root, "IdentificacionSociedad/Poblacion")
    infos["zip"] = get_text_safely(root, "IdentificacionSociedad/CodPostal")
    infos["state"] = get_text_safely(root, "IdentificacionSociedad/Provincia")
    infos["phone"] = get_text_safely(root, "DatosContacto/Telefono")
    infos["email"] = get_text_safely(
        root, "SeccionDatosGenerales/DatosContacto/Email"
    )
    infos["website"] = get_text_safely(
        root, "SeccionDatosGenerales/DatosContacto/Url"
    )
    infos["axesor_risk_score"] = get_text_safely(
        root, "Rating/RatingAxesorDef"
    )
    infos["tax_id"] = get_text_safely(root, "IdentificacionSociedad/Nif")
    infos["cnae"] = get_text_safely(
        root, "IdentificacionBalance/Sector/Cnae"
    ) or get_text_safely(root, "ActividadComercial/Cnae/CodigoSIC")
    infos["axesor_data"] = xml.dom.minidom.parseString(response).toprettyxml()
    return infos
