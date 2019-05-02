import scrapy
import pprint

GET_INFO = "Get info"
GET_OLD_REGISTRATION_INFO = "Get old registration info"
GET_QUALIFICATIONS = "Get Qualifications"
GET_CATEGORY_DETAILS = "Get Category details"
PRACTICE_STRING = "PRACTICE TYPEPRACTICE FIELDSPECIALITYSUB SPECIALITYFROM DATEORIGIN"

valid_keys = ["PERSONAL INFORMATION", "REGISTRATION INFORMATION", "QUALIFICATION INFORMATION",
              "CATEGORY DETAILS"]
valid_info = ["NAME", "CITY", "PROVINCE", "POST CODE",
              "REGISTRATION NUMBER", "REGISTRATION STATUS", "REGISTER", "BOARD"]

class RegistrationDetails:
    def __init__(self):
        self.registeration_number = ''
        self.registration_status = ''
        self.register_as = ''
        self.board = ''

        
class HealthCareWorker:
    def __init__(self):
        self.full_name = '' # ctl00_ContentPlaceHolder1_lblFullname
        self.city = '' # ctl00_ContentPlaceHolder1_lblCITY
        self.province = '' # ctl00_ContentPlaceHolder1_lblPROVINCE
        self.post_code = '' # ctl00_ContentPlaceHolder1_lblPOSTAL_CODE
        self.registeration = RegistrationDetails()
        self.qualitifications = [] #qualitification name & date obtained
        self.category_details = {} #practice type, practice field, speciality, sub speciality, from date, origin
        self.terminations = [] # List of RegistrationDetails


class HpscaSpider(scrapy.Spider):
    name = "HpscaSpider"
    start_urls = ['http://isystems.hpcsa.co.za/iregister/PractitionerView.aspx?FILENO=997034557']

    def parse(self, response):
        #print ('Ferdi printing...')
        print(response.url)
        # Get all the <table> tags
        table_selectors = response.xpath("//table")
        if len(table_selectors) < 1:
            return
        table = table_selectors[0]
        state = "Unknown"
        registration_info_count = 0
        hcw = {}
        registration_history = []
        qualifications = []
        new_regs = {}
        for tr in table.xpath('//tr'):
            key = tr.xpath('string(./td[1])').extract_first().strip().strip(': ')
            value = tr.xpath('string(./td[2])').extract_first().strip().strip(': ')
            #print('key {0}, value {1}'.format(key, value))
            if key == '' and value == '':
                continue
            if key in valid_keys:
                if key == "PERSONAL INFORMATION":
                    state = GET_INFO
                elif key == "REGISTRATION INFORMATION":
                    if registration_info_count == 0:
                        state = GET_INFO
                    else:
                        state = GET_OLD_REGISTRATION_INFO
                    registration_info_count += 1
                elif key == "QUALIFICATION INFORMATION":
                    state = GET_QUALIFICATIONS
                elif key == "CATEGORY DETAILS":
                    state = GET_CATEGORY_DETAILS
                else:
                    state = "Unknown"
            
            if state == GET_INFO and key in valid_info:
                hcw[key] = value
            elif state == GET_OLD_REGISTRATION_INFO and value != '':
                if key == "REGISTRATION NUMBER":
                    new_regs = {}
                new_regs[key] = value
                if key == "BOARD":
                    registration_history.append(new_regs)
            elif state == GET_QUALIFICATIONS and key != '' and value != '':
                qualifications.append({"name": key, "date obtained": value})
            elif state == GET_CATEGORY_DETAILS and key.startswith(PRACTICE_STRING):
                key = key.replace(PRACTICE_STRING, '').strip()
                hcw["special flags"] = key
        if len(hcw) > 0:
            hcw["Registration History"] = registration_history
            hcw["Qualifications"] = qualifications
            #print('hcw {}'.format(hcw))
        #print ('...Ferdi printing')
        yield hcw
        


