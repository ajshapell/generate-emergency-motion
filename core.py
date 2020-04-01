import json
import datetime
import requests
from docx import Document

def query_docket_api(docket_number):
    useragent = str(datetime.datetime.now().year)+str(datetime.datetime.now().month)+str(datetime.datetime.now().day)+str(datetime.datetime.now().hour)+str(datetime.datetime.now().minute)
    response = requests.get("https://services.pacourts.us/public/v1/cases/{}".format(
        str(docket_number).zfill(5)), headers={"user-agent": useragent})

    if response.status_code != 200:
        if "Case not found for docket number" in response.text:
            return "NO_DOCKET"
        else:
            return "SERVER_ERROR"
    else:
        return response.json()
    
def get_docket_values(docket_json):
    attorneys = docket_json["caseParticipantAttorneys"]
    for attorney in attorneys:
        if attorney["caseParticipantRole"]["name"] == "Defendant":
            attorney_name = attorney["participantName"]["documentName"]
            attorney_address = " ".join(attorney["caseMemberAddresses"][0]["addressLines"])
            attorney_id = attorney["paBarNumber"]

    for case_participant in docket_json["caseParticipants"]:
        if case_participant["role"]["name"] == "Defendant":
            defendant_name = case_participant["participantName"]["documentName"]

    bail_records = []
    for case_bail in docket_json["caseBails"]:
        for bail_record in case_bail["bailRecords"]:
            bail_records.append(bail_record)
    bail_amount = sorted(bail_records, key = lambda i: datetime.datetime.strptime(i['actionDate'], "%Y-%m-%dT%H:%M:%S%z"), reverse=True) 

    return {
        "ARREST_DATE": datetime.datetime.strptime(docket_json["arrestDate"], "%Y-%m-%dT%H:%M:%S%z").strftime("%B %-d, %Y") if docket_json["arrestDate"] else None,
        "ATTORNEY_NAME": attorney_name.replace(", Esq.",""),
        "ATTORNEY_ADDRESS": attorney_address,
        "ATTORNEY_ID": attorney_id,
        "BAIL_AMOUNT": '${:,.0f}'.format(bail_amount[0]["totalAmount"]),
        "CHARGES": ", ".join([o["statuteDescription"] for o in docket_json["offenses"]]),
        "COUNTY_NAME": docket_json["municipality"]["county"]["name"].upper()+" COUNTY, PENNSYLVANIA",
        "COURT_NAME": "IN THE COURT OF COMMON PLEAS",
        "CURRENT_DATE": datetime.date.today().strftime("%B %-d, %Y"),
        "DEFENDANT_NAME": defendant_name,
        "DOCKET_NUMBER": docket_json["docketNumber"],
    }

def populate_motion(docket_values):
    document = Document('motion_template.docx')

    for key, value in docket_values.items():
        value = value if value else "TBD"
        for paragraph in document.paragraphs:
            if key in paragraph.text:
                existing_txt = paragraph.text
                paragraph.text = existing_txt.replace(key,value)

    document.save('Emergency Motion for {} - {}.docx'.format(docket_values["DEFENDANT_NAME"], docket_values["DOCKET_NUMBER"]))


populate_motion(get_docket_values(query_docket_api("MJ-02302-CR-0000068-2020")))
