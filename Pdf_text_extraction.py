import PyPDF2
import sys
import os
import glob
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
import re
import pandas as pd
import time
from PIL import Image

# pip install paddleocr PyPDF2 pdf2image pandas Pillow

poppler_path = r"C:\Data Extraction BT\Supporting files\Release-24.08.0-0\poppler-24.08.0\Library\bin"
ocr = PaddleOCR(use_angle_cls=True, lang='en')

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(script_directory)
pdf_files = glob.glob("*.pdf")

img_path = "Images"
if not os.path.exists(img_path):
    os.makedirs(img_path)

def get_page_count(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    return len(reader.pages)

def only_str(txt):
    return re.sub(r"[^a-zA-Z]", "", txt).lower()

def get_coordinates(target_size, box_coords, dpi):
    # 300 dpi original =  2481, 3509
    # 300 dpi sub = 2550, 3300

    if dpi == 300:
        original_size = (2481, 3509)  # for 300 DPI
    if dpi == 400:
        original_size = (3308, 4678)  # for 300 DPI
    
    original_width, original_height = original_size
    target_width, target_height = target_size
    x0, y0, x1, y1 = box_coords

    # Calculate scaling factors
    x_scale = target_width / original_width
    y_scale = target_height / original_height

    # Convert coordinates
    x0_points = x0 * x_scale
    y0_points = y0 * y_scale
    x1_points = x1 * x_scale
    y1_points = y1 * y_scale

    return (x0_points, y0_points, x1_points, y1_points)

def first_page_finder(pdf_path, img_name, to_find):
    for page_num, page in enumerate(convert_from_path(pdf_path=pdf_path, dpi=300, poppler_path=poppler_path)):
        print("first size - ",page.size)
        if page.size == (2481, 3509):
            box_size = (50, 1300, 800, 1700)
        else:
            box_size = get_coordinates(page.size, (50, 1300, 800, 1700), 300)
        cropped_image = page.crop(box_size)
        image_output_path = os.path.join(img_path, img_name)
        cropped_image.save(image_output_path)
        result = ocr.ocr(image_output_path)
        for idx in range(len(result)):
            res = result[idx]
            if res is not None:   
                for line in res:
                    if only_str(line[1][0]) == to_find:
                        return page_num
    return None

def first_page_finder_cloa(pdf_path, img_name, to_find):
    pages = []
    for page_num, page in enumerate(convert_from_path(pdf_path=pdf_path, dpi=300, poppler_path=poppler_path)):
        if page.size == (2481, 3509):
            box_size = (650, 200, 1850, 400)
        else:
            box_size = get_coordinates(page.size, (650, 200, 1850, 400), 300)
        cropped_image = page.crop(box_size)
        image_output_path = os.path.join(img_path, img_name)
        cropped_image.save(image_output_path)
        result = ocr.ocr(image_output_path)
        for idx in range(len(result)):
            res = result[idx]
            if res is not None:   
                for line in res:
                    if only_str(line[1][0]) == to_find:
                        pages.append(page_num)
                        break
    print(pages)                    
    return pages

        

# First Page of the contract 

def first_page(pdf_path, txt_file_path, page_num):
    print("Processing First Page .....")
    image = convert_from_path(pdf_path=pdf_path, dpi=300, poppler_path=poppler_path)[page_num]
    # x0, top, x1, bottom = 50, 1000, 1600, 1600  # for 200
    if image.size == (2481, 3509):
        x0, top, x1, bottom = 75, 1500, 2400, 2400   # for 300
    else:
        x0, top, x1, bottom = get_coordinates(image.size, (75, 1500, 2400, 2400), 300)
    cropped_image = image.crop((x0, top, x1, bottom))
    image_output_path = os.path.join(img_path, "first.png")
    cropped_image.save(image_output_path)
    result = ocr.ocr(image_output_path)

    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            with open(txt_file_path, "a") as txt:
                txt.write(f"{line[1][0]}\n")
        with open(txt_file_path, "a") as txt:
            txt.write("______________________________\n")
            txt.write("\n")
    print("Extracted First Page")
    return image

# Digital Signature Extraction

def extract_sign(image, txt_file_path):
    print("Processing Digital Signature .....")
    if image.size == (2481, 3509):
        x0, top, x1, bottom = 50, 3100, 850, 3350
    else:
        x0, top, x1, bottom = get_coordinates(image.size, (50, 3100, 850, 3350), 300)
    cropped_image = image.crop((x0, top, x1, bottom))
    image_output_path = os.path.join(img_path, "sign.png")
    cropped_image.save(image_output_path)
    result = ocr.ocr(image_output_path)

    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            with open(txt_file_path, "a") as txt:
                txt.write(f"{line[1][0]}\n")
        with open(txt_file_path, "a") as txt:
            txt.write("______________________________\n")
            txt.write("\n")
    print("Extracted Digital Signature")

# Extracting the Full Page

def get_full_page(pdf_path, page_num, img_name):
    print(f"Extracting Page No: {page_num}")
    image = convert_from_path(pdf_path=pdf_path, dpi=300, poppler_path=poppler_path)[page_num]
    # x0, top, x1, bottom = 50, 100, 1500, 2080  # For 200
    if image.size == (2481, 3509):
        x0, top, x1, bottom = 75, 150, 2250, 3120  # For 300
    else:
        x0, top, x1, bottom = get_coordinates(image.size, (75, 150, 2250, 3120), 300)
    
    cropped_image = image.crop((x0, top, x1, bottom))
    image_output_path = os.path.join(img_path,img_name)
    cropped_image.save(image_output_path)
    result = ocr.ocr(image_output_path)
    print(f"Extracted Page No: {page_num}")
    return (cropped_image, result)

# Crop the Image based on keyword

def crop_image_keyword(image,result, first_word, last_word = None):
    x0, top, x1, bottom = 0 , 0, image.width, 0
    first_word = only_str(first_word)
    image_width = (50*image.width)/100
    if last_word is not None:
        last_word = only_str(last_word)
    for idx in range(len(result)):
        res = result[idx]        
        for line in res:
            if isinstance(line, list):
                word = only_str(line[1][0])
                if word == first_word and line[0][0][0] < image_width > line[0][2][0]:
                    top = line[0][0][1] - 10
                    if last_word is None:
                        bottom = image.height
                        break
                if word == last_word and line[0][0][0] < image_width > line[0][2][0]:
                    bottom = line[0][0][1] - 10
    if top == 0:
        return
    if bottom == 0:
        bottom = image.height
    print(f"Cropped image for {first_word}")
    return image.crop((x0, top, x1, bottom))

# Second Page Service Details

def get_vals(ext_list, first, second = None):

    first = only_str(first)
    if second is not None:
        second = only_str(second)
    vals = []
    for i, j in enumerate(ext_list):
        j = only_str(j)
        if j == first:
            vals.append(i+1)
            if second is None:
                vals.append(len(ext_list))
        if j == second:
            vals.append(i)
            break
    return ext_list[vals[0] : vals[1]]
        
def sep_add(li): 
    First = [j for i, j in enumerate(li) if i%2 != 0]
    Second = [j for i, j in enumerate(li) if i%2 == 0]
    return First, Second

def majority_range(input_range, predefined_ranges):  

    for key, (low, high) in predefined_ranges.items():
        # Check if more than half of input range lies within a predefined range
        overlap_start = max(input_range[0], low)
        overlap_end = min(input_range[1], high)
        overlap = max(0, overlap_end - overlap_start)
        if overlap > (input_range[1] - input_range[0]) / 2:
            return key
    return None

def second_service_charges(txt_file_path):
    image_output_path = os.path.join(img_path, "service_details.png")

    result = ocr.ocr(image_output_path)

    # columns = ['User Feature Packs', 'Contract Term', 'Care Option', 'Call Plans', 'Sites']

    service_details = []

    for idx in range(len(result)):
        res = result[idx]    
        for line in res:
            service_details.append(line[1][0])

    service_details.pop(0)
            
    with open(txt_file_path, "a") as txt:
        txt.write("Service Details\n\n")
        txt.write(f"User Feature Packs  ---->       {get_vals(service_details, 'User Feature Packs', 'Contract Term')}\n")
        txt.write(f"Contract Term       ---->       {get_vals(service_details, "Contract Term", "Care Option")}\n")
        txt.write(f"Care Option         ---->       {get_vals(service_details, 'Care Option', 'Call Plans')}\n")
        txt.write(f"Call Plans          ---->       {get_vals(service_details, 'Call Plans', 'Sites')}\n")
        txt.write(f"Sites               ---->       {get_vals(service_details, 'Sites')}\n")
        
        txt.write("\n\n")
    with open(txt_file_path, "a") as txt:
        txt.write("______________________________\n")
        txt.write("\n")       
    print("Extracted Service Charges")

def is_within_percentage_range(previous, next):
    previous = (previous[1] + previous[0])//2    
    min_val, max_val = next
    lower_bound = min_val + 0.4 * (max_val - min_val)
    upper_bound = min_val + 0.6 * (max_val - min_val)
    
    return lower_bound <= previous <= upper_bound

def df_conversion(image_name, image_type, txt_file_path):

    image_output_path = os.path.join(img_path, image_name)

    result = ocr.ocr(image_output_path)

    table_map = {  "Product" : 0,
            "Quantity" : 0,
            "Initial" : 0,
            "Recurring" : 0 } 

    def strip_spaces(word):
        return word.strip()

    for idx in range(len(result)):
        res = result[idx]    
        for line in res:
            if strip_spaces(line[1][0]) == "Product":
                table_map["Product"] = line[0][0][0]
            if strip_spaces(line[1][0]) == "Quantity":
                table_map["Quantity"] = (line[0][0][0], line[0][1][0])
            if strip_spaces(line[1][0]) == "Initial":
                table_map["Initial"] = (line[0][0][0], line[0][1][0])
            if strip_spaces(line[1][0]) == "Recurring":
                table_map["Recurring"] = (line[0][0][0], line[0][1][0])
    table_map["Product"] = (table_map["Product"], table_map["Quantity"][0]-30)
    table_map["Initial"] = (table_map["Quantity"][1]+ 40, table_map["Initial"][1])

    table_vals = []
    for idx in range(len(result)):
        res = result[idx]    
        for line in res:
            print(line)
            table_vals.append((line[1][0],(line[0][0][0], line[0][1][0]), (line[0][0][1], line[0][2][1])))

    table_vals = table_vals[5:]

    df = pd.DataFrame(columns=["Product","Quantity","Initial", "Recurring"])

    counter = 0
    for i, j in enumerate(table_vals):
        if i != 0:
            if not is_within_percentage_range(table_vals[i-1][2],j[2]):
                counter+=1
        column = majority_range(j[1],table_map)
        if counter in df.index and pd.notna(df.loc[counter, column]):
            df.at[counter, column] = df.at[counter, column] + "-" + j[0]
        else:
            df.at[counter, column] = j[0]

    with open(txt_file_path, "a") as txt:
        txt.write(f"{image_type}\n\n")
        df_string = df.to_string(header=True, index=False)
        txt.write(df_string)
        txt.write("\n\n")
    with open(txt_file_path, "a") as txt:
        txt.write("______________________________\n")
        txt.write("\n")    
    print(f"Extracted {image_type}")

# Third page site details

def third_site_details(txt_file_path):
    image_output_path = os.path.join(img_path, "site_details.png")

    result = ocr.ocr(image_output_path)

    site_details = []
    for idx in range(len(result)):
        res = result[idx]    
        for line in res:
            site_details.append(line[1][0])

    # columns=["Site Name", "Contact", "Address", "User Feature Packs", "Initial Charges", "Recurring Charges", "Required Date"]
    # sub_columns = ["Delivery", "Installation"]

    site_details.pop(0)

    with open(txt_file_path, "a") as txt:
        txt.write("Site Details\n\n")
        txt.write(f"Site Name           ---->       {get_vals(site_details, "Site Name", "Contact")}\n")
        txt.write(f"Contact             ---->       {get_vals(site_details, "Contact", "Address")}\n")
        txt.write(f"Address             ---->\n")
        try: 
            tt = get_vals(site_details, "Address", "User Feature Packs")
        except IndexError as e:
            tt = get_vals(site_details, "Address", "User Feature")
        txt.write(f"           Delivery     ---->  {sep_add(tt[2:])[0]}\n")      
        txt.write(f"           Installation ---->  {sep_add(tt[2:])[1]}\n")
        try: 
            tt = get_vals(site_details, "User Feature Packs", "Initial Charges")
        except IndexError as e:
            tt = get_vals(site_details, "User Feature", "Initial Charges")        
        txt.write(f"User Feature Packs  ---->       {tt}\n")
        try: 
            tt = get_vals(site_details, "Initial Charges", "Recurring Charges")
        except IndexError as e:
            tt = get_vals(site_details, "Initial Charges", "Recurring")       
        txt.write(f"Initial Charges     ---->       {tt}\n")
        try: 
            tt = get_vals(site_details, "Recurring Charges", "Required Date")
        except IndexError as e:
            tt = get_vals(site_details, "Recurring", "Required Date")  
        txt.write(f"Recurring Charges   ---->       {tt}\n")
        txt.write(f"Required Date       ---->       {get_vals(site_details, "Required Date")}\n")
        txt.write("\n\n")
    with open(txt_file_path, "a") as txt:
        txt.write("______________________________\n")
        txt.write("\n")
    print("Extracted Site Details")

def extract(pdf_path,pg, img_path, txt_file_path, start_time):
    # ocr = PaddleOCR(use_angle_cls=True, lang='en',rec_algorithm ="SVTR_LCNet",table=True,det_db_box_thresh=0.5,det_db_unclip_ratio=2.2,show_log=False)
    image_output_path = os.path.join(img_path, "pro_img.png")
    convert_from_path(pdf_path,dpi=400, poppler_path=poppler_path)[pg].save(image_output_path)
    start=0
    im = Image.open(image_output_path)
    print("CLOA size",im.size)
    im = im.crop((286,145,3206,825))
    image_output_path = os.path.join(img_path, "test_pdf_type.png")
    im.save(image_output_path)
    result = ocr.ocr(image_output_path, cls=True)
    kcheck=[]
    try:
        for line in result[0]:
            kcheck.append(line[1][0].lower())
    except:
        pass
    result = result[0]
    for i in kcheck:
        if 'cloa' in i:
            start=1
            break
    if start==1:
        image_output_path = os.path.join(img_path, "pro_img.png")
        im = Image.open(image_output_path)
        im = im.crop((312,965,3229,2022))
        image_output_path = os.path.join(img_path, "test.png")
        im.save(image_output_path)
        result = ocr.ocr(image_output_path, cls=True)
        k=[]
        try:
            for line in result[0]:
                k.append(line[1][0])
        except:
            pass
        result = result[0]
        g={"number":[],"company_name":[],"sign_type":[],"print_name":[],"doc_date":[],"sign_data_1":[],"sign_data_2":[],"sign_data_3":[]}
        flg=[0,0,0,0,0,0,0,0,0]
        for i in range(len(k)):
            if flg[0]==0:
                try:
                    if "BuildingName/" in k[i].strip().replace(" ","") :
                        if k[i+2].strip().isnumeric() and len(k[i+2].strip()) ==11 :
                            g["number"].append(k[i+2].strip())
                            flg[0]+=1
                except:
                    pass
            if flg[1]==0:
                try:
                    if "Number" in k[i].strip() :
                        if k[i+1].strip().isnumeric() and len(k[i+1].strip()) ==11 :
                            g["number"].append(k[i+1].strip())
                            flg[1]+=1
                except:
                    pass
        image_output_path = os.path.join(img_path, "pro_img.png")
        im = Image.open(image_output_path)
        im = im.crop((178,1696,3150,2733))
        image_output_path = os.path.join(img_path, "test1.png")
        im.save(image_output_path)
        result = ocr.ocr(image_output_path, cls=True)
        k1=[]
        try:
            for line in result[0]:
                k1.append(line[1][0])
        except:
            pass
        result = result[0]
        for i in range(len(k1)):
            if flg[2]==0:
                try:
                    if "CompanyName" in k1[i].strip().replace(" ","") :
                        if "BillingAddress" not in k1[i+1].strip().replace(" ","") :
                            g["company_name"].append(k1[i+1].strip())
                            flg[2]+=1
                except:
                    pass
        image_output_path = os.path.join(img_path, "pro_img.png")
        im = Image.open(image_output_path)
        im = im.crop((207,2745,1434,3863))
        image_output_path = os.path.join(img_path, "test2.png")
        im.save(image_output_path)
        result = ocr.ocr(image_output_path, cls=True)
        k2=[]
        try:
            for line in result[0]:
                k2.append(line[1][0])
        except:
            pass
        result = result[0]
        for i in range(len(k2)):
            if flg[3]==0:
                try:
                    if "Signed" in k2[i].strip() :
                        if "PrintName" not in k2[i+1].strip().replace(" ","") :
                            g["sign_type"].append(k2[i+1].strip())
                            flg[3]+=1
                except:
                    pass
            if flg[4]==0:
                try:
                    if "PrintName" in k2[i].strip().replace(" ","")  :
                        if k2[i+1].strip()!= "":
                            g["print_name"].append(k2[i+1].strip())
                            flg[4]+=1
                except:
                    pass
            if flg[5]==0:
                try:
                    if "Date(DD/MM/YY)" in k2[i].strip().replace(" ","") :
                        if k2[i+1].strip()!= "" and "Email" not in k2[i+1].strip() :
                            g["doc_date"].append(k2[i+1].strip())
                            flg[5]+=1
                except:
                    pass
        image_output_path = os.path.join(img_path, "pro_img.png")
        im = Image.open(image_output_path)
        im = im.crop((108,3826,1638,4565))
        image_output_path = os.path.join(img_path, "test3.png")
        im.save(image_output_path)
        result = ocr.ocr(image_output_path, cls=True)
        k3=[]
        try:
            for line in result[0]:
                k3.append(line[1][0])
        except:
            pass
        result = result[0]
        if len(k3) > 2:
            if flg[6]==0:
                try:
                    if k3[0].strip()!= "" and "xl" not in k3[0].strip() and "Document" not in k3[0].strip() :
                        g["sign_data_1"].append(k3[0].strip())
                    if k3[1].strip()!= "" and "xl" not in k3[1].strip() and "Document" not in k3[1].strip():
                        g["sign_data_2"].append(k3[1].strip())
                    if k3[2].strip()!= "" and "xl" not in k3[2].strip() and "Document" not in k3[2].strip():
                        g["sign_data_3"].append(k3[2].strip())
                    flg[6]+=1
                except:
                    pass
        col=[i for i in g.keys()]
        val=[','.join(i) for i in g.values()]
        df=pd.DataFrame({"column":col,"values":val})
        with open(txt_file_path, "a") as txt:
            txt.write("CLOA\n\n")
            df_string = df.to_string(header=True, index=False)
            txt.write(df_string)
            txt.write("\n\n")
        with open(txt_file_path, "a") as txt:
            txt.write("______________________________\n")
            txt.write("\n")
        remove_folder(img_path)
        end_time = time.time()
        total_time = end_time - start_time
        print(f"The total time taken to extract the CLOA {pdf_path} is {int(total_time//60)} minute and {int(total_time%60)} seconds." )

def remove_folder(folder_path):
    # shutil.rmtree(folder_path, ignore_errors=True)
    for i in os.listdir(folder_path):
        os.remove(os.path.join(folder_path, i))

def extraction_order(pdf_path, txt_file_path, page_num, start_time):
    extract_sign(first_page(pdf_path, txt_file_path, page_num), txt_file_path)
    page_4 = get_full_page(pdf_path, page_num + 4, "full.png")
    cropped_image, result = page_4[0], page_4[1]
    crop_image_keyword(cropped_image, result, "service details","service charges").save(os.path.join(img_path,"service_details.png"))
    crop_image_keyword(cropped_image, result, "service charges", "training").save(os.path.join(img_path,"service_charges.png"))
    if crop_image_keyword(cropped_image, result, "training") is not None:
        crop_image_keyword(cropped_image, result, "training").save(os.path.join(img_path,"training.png"))
    second_service_charges(txt_file_path)
    df_conversion("service_charges.png", "Service Charges", txt_file_path)
    if os.path.exists(os.path.join(img_path,"training.png")):
        df_conversion("training.png", "Training", txt_file_path)

    page_5 = get_full_page(pdf_path, page_num + 5, "full_2.png")
    cropped_image, result = page_5[0], page_5[1]
    crop_image_keyword(cropped_image, result, "site details", "user feature packs & add ons").save(os.path.join(img_path,"site_details.png"))
    crop_image_keyword(cropped_image, result, "user feature packs & add ons", "phones & peripherals").save(os.path.join(img_path,"user_feature_packs.png"))
    crop_image_keyword(cropped_image, result, "phones & peripherals", "numbers" ).save(os.path.join(img_path,"phones_peripherals.png"))
    crop_image_keyword(cropped_image, result, "numbers" ).save(os.path.join(img_path,"numbers.png"))
    third_site_details(txt_file_path)
    df_conversion("user_feature_packs.png", "User Feature Packs", txt_file_path) 
    df_conversion("phones_peripherals.png", "Phones Peripherals", txt_file_path)
    df_conversion("numbers.png", "Numbers", txt_file_path)
    remove_folder(img_path)
    end_time = time.time()
    total_time = end_time - start_time
    print(f"The total time taken to extract the {pdf_path} is {int(total_time//60)} minute and {int(total_time%60)} seconds." )

def wrapper():

    for pdf in pdf_files:
        count = get_page_count(pdf)
        if count == 13:
            start_time = time.time()
            txt_file_path = os.path.splitext(pdf)[0] + ".txt"
            extraction_order(pdf_path= pdf, txt_file_path = txt_file_path, page_num = 0, start_time=start_time)
        if count >= 14:
            start_time = time.time()
            txt_file_path = os.path.splitext(pdf)[0] + ".txt"
            page_num = first_page_finder(pdf_path = pdf, img_name =  "test.png", to_find = "instrictestconfidence")
            extraction_order(pdf_path= pdf, txt_file_path = txt_file_path, page_num = page_num, start_time=start_time)
            
            # Find CLOA and append 
            start_time = time.time()
            page_num = first_page_finder_cloa(pdf_path =pdf, img_name = "test_2.png", to_find = "customerletterofauthoritycloa")
            end_time = time.time()
            total_time = end_time - start_time
            print(f"The total time taken find all the CLOA pages {int(total_time//60)} minute and {int(total_time%60)} seconds." )
            
            if page_num:
                for i in page_num:
                    start_time = time.time()
                    extract(pdf_path = pdf, pg = i, img_path = img_path, txt_file_path= txt_file_path, start_time = start_time)                    
            else:
                print("No CLOA found")

        if count == 1:
            start_time = time.time()
            txt_file_path = os.path.splitext(pdf)[0] + ".txt"
            extract(pdf_path = pdf, pg = 0, img_path = img_path, txt_file_path= txt_file_path, start_time = start_time)
wrapper()
