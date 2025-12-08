#this file includes the rent value for each product, like what percene tis the rent for a perticular product

# Percentage rent applied on product price per day
RENT_RATE = 0.002     # 2% per day
# GST / Tax applied on total rent
GST_RATE = 0.18      # 18% GST
# You can add more config constants later if needed:
# TAX_RATE = 0.05
# DISCOUNT_RATE = 0.10
# PDF_STORAGE_PATH = "invoices/"


#----RENT FORMULA----
# days_in_inventory = (today_date - product.created_at).days

# line_total = unit_price * qty
# daily_rent = line_total * RENT_RATE
# item_rent = daily_rent * days_in_inventory
#------For full invoice:---
# subtotal_rent = sum(line_total of all items)
# total_rent = sum(item_rent of all items)