import requests
import xml.etree.ElementTree as ET
import xml.dom.minidom
import hashlib


def search_parse(response:str):
    root = ET.fromstring(response)
    companies = root.findall("./ListaPaquetesNegocio/ListaSociedades/Sociedad",{"":"*"})
    companies_infos = []
    for company in companies:
        company_infos = {}
        company_infos["name"] = company.findall("./NombreSociedad",{"":"*"})[0].text
        company_infos["coreff_company_code"] = company.findall("./Cif",{"":"*"})[0].text
        company_infos["axesor_internal_id"] = company.get("CodInfotel")
        companies_infos.append(company_infos)
    return companies_infos

def search_by_name(user, password, company_name):
    proxies = {
        "http":"",
        "https":"",
    }
    params = {"cod_usuario": user, "accion": "3"}
    params.update({"nombreSociedad": company_name})

    cadena = "".join(params.values())
    digest = hashlib.sha3_256((cadena + password).encode("iso-8859-1")).hexdigest()
    params["crc"] = digest

    res = requests.get("https://www.axesor.es/buscador-unificado", params=params, proxies=proxies)
    return search_parse(res.text)

def search_by_code(user, password, code):
    proxies = {
        "http":"",
        "https":"",
    }
    params = {"cod_usuario": user, "cod_servicio": "388", "cod_idioma": "2"}
    params.update({"cif": code})

    cadena = "".join(params.values())
    digest = hashlib.sha3_256((cadena + password).encode("iso-8859-1")).hexdigest()
    params["crc"] = digest

    res = requests.get("https://informes.axesor.es/informe", params=params, proxies=proxies)
    return search_parse(res.text)

def get_infos(user, password, code):
    proxies = {
        "http":"",
        "https":"",
    }
    params = {"cod_usuario": user, "cod_servicio": "388", "cod_idioma": "2"}
    params.update({"cif": code})

    cadena = "".join(params.values())
    digest = hashlib.sha3_256((cadena + password).encode("iso-8859-1")).hexdigest()
    params["crc"] = digest

    res = requests.get("https://informes.axesor.es/informe", params=params, proxies=proxies)
    return parse_infos(res.text)

def parse_infos(response:str):
    root = ET.fromstring(response)[0]
    infos = {}
    infos["street"] = root.findall("./ListaDelegaciones/Delegacion/Domicilio", {"":"*"})[0].text
    infos["city"] = root.findall("./ListaDelegaciones/Delegacion/Municipio", {"":"*"})[0].text
    infos["zip"] = root.findall("./ListaDelegaciones/Delegacion/CodigoPostal", {"":"*"})[0].text
    infos["country"] = root.findall("./ListaVentaGeografia/VentaGeografia/Pais", {"":"*"})[0].attrib["NombrePais"]
    infos["phone"] = root.findall("./SeccionDatosGenerales/DatosContacto/Telefono", {"":"*"})[0].text
    infos["email"] = root.findall("./SeccionDatosGenerales/DatosContacto/Email", {"":"*"})[0].text
    infos["website"] = root.findall("./SeccionDatosGenerales/DatosContacto/Url", {"":"*"})[0].text
    infos["axesor_risk_score"] = root.findall("./Rating/RatingAxesorDef", {"":"*"})[0].text
    infos["tax_id"] = root.findall("./IdentificacionBalance/IdentificacionSociedad/Nif", {"":"*"})[0].text
    infos["axesor_data"] = xml.dom.minidom.parseString(response).toprettyxml()
    return infos

