import datetime as dt
from dateutil.relativedelta import relativedelta
from docx2pdf import convert
import matplotlib.pyplot as plt
from docxtpl import DocxTemplate, InlineImage
import pymysql

import settings

global user_id, report_address, report_type, report_item, report_duration

dates = []
invoices = []
items = []
types = []
prices = []
store_names = []
store_address = []
total = 0
no_items = 0
no_invoices = 0
no_warranties = 0

salesTblRows = []

user_id = settings.user_id
report_address = settings.report_address
report_type = settings.report_type
report_item = settings.report_item
report_duration = settings.report_duration

duration = dt.date.today() - relativedelta(months=int(report_duration))

conn = pymysql.connect(host='localhost', user='root', password='toor')
cursor = conn.cursor()

query = 'use DB'
cursor.execute(query)

if report_address != "" and report_duration != 0 and report_item != "" and report_type != "":
    query = "SELECT * FROM invoice WHERE store_address LIKE %s AND invoice_date >= %s"
    cursor.execute(query, (f"%{report_address}%", duration))
    invoice = cursor.fetchall()

    query = "SELECT * FROM items WHERE item_type LIKE %s AND item_name LIKE %s"
    cursor.execute(query, (f"%{report_type}%", f"%{report_item}%"))
    item = cursor.fetchall()

elif report_address != "" and report_duration != 0 and report_item != "" and report_type == "":
    query = "SELECT * FROM invoice WHERE store_address LIKE %s AND invoice_date >= %s"
    cursor.execute(query, (f"%{report_address}%", duration))
    invoice = cursor.fetchall()

    query = "SELECT * FROM items WHERE item_name LIKE %s "
    cursor.execute(query, f"%{report_item}%")
    item = cursor.fetchall()

    query = "SELECT * FROM warranty WHERE store_address LIKE %s AND starting_date >= %s AND warranty_items LIKE %s"
    cursor.execute(query, (f"%{report_address}%", duration, f"%{report_item}%"))
    warranty = cursor.fetchall()

elif report_address != "" and report_duration != 0 and report_type != "" and report_item == "":
    query = "SELECT * FROM items WHERE item_type LIKE %s"
    cursor.execute(query, f"%{report_type}%")
    item = cursor.fetchall()

elif report_address != "" and report_duration != 0 and report_type == "" and report_item == "":
    query = "SELECT * FROM invoice WHERE store_address LIKE %s AND invoice_date >= %s"
    cursor.execute(query, (f"%{report_address}%", duration))
    invoice = cursor.fetchall()

    query = "SELECT * FROM warranty WHERE store_address LIKE %s AND starting_date >= %s"
    cursor.execute(query, (f"%{report_address}%", duration))
    warranty = cursor.fetchall()

    item = ()

elif report_address == "" and report_duration != 0 and report_item != "" and report_type != "":
    query = "SELECT * FROM invoice WHERE invoice_date >= %s"
    cursor.execute(query, duration)
    invoice = cursor.fetchall()

elif report_address == "" and report_duration != 0 and report_item == "" and report_type != "":
    query = "SELECT * FROM invoice WHERE invoice_date >= %s"
    cursor.execute(query, duration)
    invoice = cursor.fetchall()

    query = "SELECT * FROM items WHERE item_name LIKE %s"
    cursor.execute(query, f"%{report_item}%")
    item = cursor.fetchall()

elif report_address == "" and report_duration != 0 and report_item != "" and report_type == "":
    query = "SELECT * FROM invoice WHERE invoice_date >= %s"
    cursor.execute(query, duration)
    invoice = cursor.fetchall()

    query = "SELECT * FROM items WHERE item_name LIKE %s"
    cursor.execute(query, f"%{report_item}%")
    item = cursor.fetchall()

    query = "SELECT * FROM warranty WHERE warranty_items LIKE %s AND starting_date >= %s"
    cursor.execute(query, (f"%{report_item}%", duration))
    warranty = cursor.fetchall()

elif report_address != "" and report_duration != 0 and report_item == "" and report_type == "":
    query = "SELECT * FROM invoice WHERE store_address LIKE %s AND invoice_date >= %s"
    cursor.execute(query, (f"%{report_address}%", duration))
    invoice = cursor.fetchall()

    query = "SELECT * FROM warranty WHERE store_address LIKE %s AND starting_date >= %s"
    cursor.execute(query, (f"%{report_address}%", duration))
    warranty = cursor.fetchall()

    for i in invoice:
        invoices.append(i[0])
        dates.append(i[2])
        store_names.append(i[4])
        store_address.append(i[5])

    for i in invoices:
        query = "SELECT * FROM items WHERE invoice_id = %s"
        cursor.execute(query, i)
        content = cursor.fetchone()
        if content != ():
            items.append(content[2])
            types.append(content[3])
            prices.append(content[4])
            no_invoices += 1
    item = ()

for i in invoice:
    if item != ():
        invoices.append(i[0])
        dates.append(i[2])
        store_names.append(i[4])
        store_address.append(i[5])

for i in invoices:
    query = "SELECT * FROM items WHERE invoice_id = %s"
    cursor.execute(query, i)
    content = cursor.fetchone()
    if content != ():
        items.append(content[2])
        types.append(content[3])
        prices.append(content[4])
        no_invoices += 1
        print('i2')

for i in warranty:
    salesTblRows.append({"date": i[4], "name": i[2], "item_type": "", "price": i[3], "store_name": i[6], "address": i[7]})
    no_warranties += 1

no_items = no_invoices + no_warranties

# create a document object
doc = DocxTemplate("MerchantReportTemplate.docx")

# create data for reports
info = []
for k in range(len(invoices)):
    date = [i for i in dates]
    name = [i for i in items]
    item_type = [i for i in types]
    prices = [i for i in prices]
    store_names = [i for i in store_names]
    store_address = [i for i in store_address]
    salesTblRows.append({"date": date[k], "name": items[k], "item_type": item_type[k], "price": prices[k], "store_name": store_names[k], "address": store_address[k]})

for i in salesTblRows:
    total += i["price"]

salesTblRows.sort(key=lambda x: x.get('date'))

info.append({"no_items": no_items, "total": total, "no_invoices": no_invoices, "no_warranties": no_warranties})

topItems = [x["name"] for x in sorted(salesTblRows, key=lambda x: x["price"], reverse=True)][0:3]

todayStr = dt.datetime.now().strftime("%d-%b-%Y")
timeStr = dt.datetime.now().strftime("%H_%M")

# create context to pass data to template
context = {
    "reportDtStr": todayStr,
    "salesTblRows": salesTblRows,
    "info": info,
    "topItemsRows": topItems
}

report_date = dt.datetime.now().strftime("%Y%m%d")
report_time = dt.datetime.now().strftime("%H:%M:%S")

# inject image into the context
fig, ax = plt.subplots()
ax.plot([x["date"] for x in salesTblRows], [x["price"] for x in salesTblRows])
if report_address != "":
    plt.title(f"Sales in {report_address}")
else:
    plt.title("Sales")
plt.xlabel("Date")
plt.ylabel("Price")
ax.xaxis.set_label_coords(1, -.1)
ax.xaxis.label.set_color('red')
ax.yaxis.label.set_color('red')
plt.xticks([x["date"] for x in salesTblRows], rotation='vertical')
fig.savefig("FigureImg.png")
context['Img'] = InlineImage(doc, 'FigureImg.png')

# render context into the document object
doc.render(context)

# save the document object as a Word file
reportWordPath = f'report_{todayStr}_{timeStr}.docx'
doc.save(reportWordPath)

# convert the Word file as pdf file
convert(reportWordPath)

pdf_file_name = reportWordPath.replace(".docx", ".pdf")
settings.pdf_file_name = pdf_file_name

query = "INSERT INTO report (user_id, report_date, report_time, report_duration, report_region, report_file) values(%s,%s,%s,%s,%s,%s)"
cursor.execute(query, (user_id, report_date, report_time, int(report_duration), report_address, pdf_file_name))
conn.commit()
