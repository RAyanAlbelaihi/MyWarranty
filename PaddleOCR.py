from paddleocr import PaddleOCR

try:
    from PIL import Image
except ImportError:
    import Image
import re


# Paddleocr
ocr = PaddleOCR(use_angle_cls=True, lang='en')
img_path = 'jarir2.jpg'
result = ocr.ocr(img_path, cls=True)
for idx in range(len(result)):
    res = result[idx]

receipt_ocr = {}

date = ''
invoice_num = ''
amount = ''
address = ''
company_name = ''
item_list = []
item_price = []
serial_number = ''
provider_name = ''


def get_address(extracted_text):
    global address
    pattern = r'((?i)address|street|road|block|saudi arabia|riyadh|city|area|county|exit|king|p.o box|location|state|region|province|zip|postal)'
    pattern = re.compile(pattern)
    matches = pattern.finditer(extracted_text)
    for match in matches:
        address = extracted_text
    receipt_ocr['Address'] = address


def get_invoice_number(extracted_text, nextline):
    global invoice_num
    pattern = (r'((?i)invoice#|invoice|bill|inv|inc|doc|document|order|ord|receipt|billing|token|trn|transaction|trx|tally|statement)')
    pattern = re.compile(pattern)
    matches = pattern.finditer(extracted_text)
    for match in matches:
        invoice_num = ''.join(c for c in extracted_text if c in '0123456789-/')
        if invoice_num == '':
            invoice_num = ''.join(c for c in nextline if c in '0123456789-/')
    receipt_ocr['InvoiceNumber'] = invoice_num


def get_date(extracted_text):
    global date
    date_pattern = r'((?i)date)'
    pattern = re.compile(date_pattern)
    matches = pattern.finditer(extracted_text)
    for match in matches:
        try:
            dateindex = extracted_text.find(match.group()) + len(match.group())
            if extracted_text[dateindex] in ['#', ':', ' ']:
                dateindex += 1
            date = extracted_text[dateindex:]
        except:
            pass
    if date == '':
        # regex for date. The pattern in the receipt is in 00.00.0000 in DD:MM:YYYY
        date_pattern = r'[\d]{1,2}/[\d]{1,2}/[\d]{4}|[\d]{1,2}-[\d]{1,2}-[\d]{2}|(\d{1,2} (?:jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec) \d{4})|[\d]{1,2}-[\d]{1,2}-[\d]{4}|[\d]{4}-[\d]{1,2}-[\d]{1,2}|[\d]{1,2}/[\d]{1,2}/[\d]{2}'
        pattern = re.compile(date_pattern)
        matches = pattern.finditer(extracted_text)
        for match in matches:
            date = match.group()
    receipt_ocr['Date'] = date


def get_total(extracted_text, nextline):
    global amount
    total_pattern = r'((?i)balance due|total amount|total tender|grand total|balance|sar|sr|riyal|^total)'
    pattern = re.compile(total_pattern)
    matches = pattern.finditer(extracted_text)
    for match in matches:
        amount = ''.join(c for c in extracted_text if c in '0123456789,.')
        if amount == '':
            amount = ''.join(c for c in nextline if c in '0123456789,.')
    receipt_ocr['Amount'] = amount


def get_companyname(extracted_text):
    global company_name
    pattern = r'((?i)store|stores|market|super market|shop|restaurant|ltd|llc|bookstore|grocery|cafe|coffee shop|retail|plumbing|workshop|industry|cafeteria)'
    pattern = re.compile(pattern)
    matches = pattern.finditer(extracted_text)
    for match in matches:
        company_name = extracted_text
    receipt_ocr['CompanyName'] = company_name


def get_items(extracted_text, nextline):
    global item_list, item_price
    if re.findall(r'^([[a-z\sA-Z]{3,})', extracted_text) and re.search(r'(\d+[.,‚]\d\d)', nextline):
        if re.search("eft|credit card|vat|tax|tax-code|change|cash|subtotal|sub-total|sub total|sales|table|name|refund|refunds|thank|by|cashier|paid|visa|mada|approved|signature|returns|helped|amount|balance|total|credit", extracted_text.lower()):
            pass
        else:
            item_list.append(extracted_text)
            pattern = r'(\d+[.,‚]\d+)'
            pattern = re.compile(pattern)
            matches = pattern.finditer(nextline)
            for match in matches:
                item_price.append(match.group())


def get_provider(extracted_text, nextline):
    global provider_name
    provider_pattern = r'((?i)warranted by|supplier|supplier name|provider name|provider|warranty provider)'
    pattern = re.compile(provider_pattern)
    matches = pattern.finditer(extracted_text)
    for match in matches:
        providerindex = extracted_text.find(match.group()) + len(match.group())
        stopindex = extracted_text.find(',')
        if stopindex == -1:
            stopindex = extracted_text.find('.')
        for i in extracted_text[providerindex:]:
            if extracted_text[providerindex] in ['#', ':', ' ']:
                providerindex += 1
        if stopindex == -1:
            stopindex = len(extracted_text)
        provider_name = extracted_text[providerindex:stopindex]
        if provider_name == '':
            provider_name = nextline
    receipt_ocr['ProviderName'] = provider_name


def get_serial(extracted_text):
    global serial_number
    serial_number_pattern = r'((?i)s/n|sn number|serial number|device serial|serial #|serial)'
    pattern = re.compile(serial_number_pattern)
    matches = pattern.finditer(extracted_text)
    for match in matches:
        serialindex = extracted_text.find(match.group()) + len(match.group())
        if extracted_text[serialindex] in ['#', ':', ' ']:
            serialindex += 1
        serial_number = extracted_text[serialindex:]
    receipt_ocr['SerialNumber'] = serial_number


# Parser
for i in range(len(res)):
    try:
        if date == '':
            get_date(res[i][1][0])
            dateindex = i
        if invoice_num == '':
            get_invoice_number(res[i][1][0], res[i+1][1][0])
            invoiceno_index = i
        if amount == '':
            get_total(res[i][1][0], res[i+1][1][0])
            amountindex = i
        if address == '':
            get_address(res[i][1][0])
            addressindex = i
        if company_name == '':
            get_companyname(res[i][1][0])
            nameindex = i
        if serial_number == '':
            get_serial(res[i][1][0])
        if provider_name == '':
            get_provider(res[i][1][0], res[i+1][1][0])
        get_items(res[i][1][0], res[i+1][1][0])
    except:
        pass


print(receipt_ocr)
print('Items: ', item_list)
print('Item Price: ', item_price)

'''for i in range(len(res)):
    print(res[i][1][0])'''
