import cv2 
import matplotlib.pyplot as plt 
import numpy as np 
import os 
from datetime import date 
from mpl_toolkits.mplot3d import Axes3D 
from selenium import webdriver 
from sklearn.cluster import KMeans 
from fpdf import FPDF

######################################### FUNKCJE
def rgb_hex(rgb):
    colors = "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    return colors

def hex_rgb(hex):
    hex = hex.lstrip('#')
    red, green, blue = bytes.fromhex(hex)
    return red, green, blue

def operations(x):
    reshape_image(get_image(destination(x)))
    pdf(location, x)

def destination(x):
    global location
    location = os.path.join(os.getcwd(), x)
    png_location= screen_capture(x)
    return png_location

def screen_capture(x):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('disable-gpu')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    driver.get('http://www.'+x)
    if not os.path.exists(location):
       os.makedirs(location)
    png_location = ''.join([location, '\\'+x+'.png'])
    driver.save_screenshot(png_location)
    print('Zapisano zrzut ekranu '+x)
    driver.quit()
    return png_location

def get_image(x):
    image = cv2.imread(x)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    print('Stworzono mapę pixeli.')
    return image

def reshape_image(image):
    reform = image.reshape((image.shape[0] * image.shape[1], 3))
    cluster = KMeans(int(5)).fit(reform)
    fig = plt.figure()
    ax = Axes3D(fig)
    colors=cluster.cluster_centers_
    red,green,blue = [np.squeeze(arr) for arr in (np.hsplit(reform,reform.shape[1]))]
    ax.scatter(red, green, blue)
    print('Rozrzucono pixele na tablicy trójwymiarowej.')
    print('Trwa zapisywanie danych.')
    plt.savefig(''.join([location, '\\fig1.png']))
    dominant_colors(cluster, colors)

def dominant_colors(cluster, centroids):
    labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    (hist, _) = np.histogram(cluster.labels_, bins = labels)
    hist = hist.astype("float")
    hist /= hist.sum()
    colors = sorted([(percent, color) for (percent, color) in zip(hist, centroids)])
    fig = plt.figure()
    ax = Axes3D(fig)
    print('Wykaz procentowy kolorów zdjęcia.')
    #if not os.path.exists(\
    fopen = open(''.join([location, '\\colors.txt']), 'w+')
    for (percent, color) in colors:
            fopen.write(''.join([rgb_hex(color)," ","{:0.2f}%".format(percent * 100),'\n']))
            ax.scatter(color[0], color[1], color[2], color = rgb_hex(color))
    fopen.close()
    plt.savefig(''.join([location, '\\fig2.png']))
    return colors

def pdf(location, x):
    print('Trwa generowanie pliku pdf.')
    pdf = FPDF()
    pdf.add_page()
    pdf.set_xy(0, 0)
    pdf.set_font('arial', style = '', size = 14)
    pdf.cell(40)
    logo = ''.join([location, '\\'+x+'.png'])
    pdf.image(logo, x = 90, y = 15, w=pdf.w/2.0, h=pdf.h/5.0)
    pdf.ln(5)
    pdf.cell(40, 20, 'Raport ze strony '+x)
    pdf.ln(10)
    pdf.cell(30, 15, str(date.today()))
    pdf.ln(65)
    pdf.cell(0, 15, 'Kolory:')
    pdf.ln(15)
    for line in open(''.join([location, '\\colors.txt'])):
        colors = line.split(" ")
        red, green, blue= hex_rgb(colors[0])
        pdf.set_fill_color(red, green, blue)
        pdf.cell(30,15,' ',fill =True)
        pdf.cell(30,15,str(colors[0]),fill =False)
        pdf.cell(20)
        pdf.cell(10,15,str(colors[1]),fill=False)
        pdf.ln(15)
    pdf.ln(15)
    pdf.cell(15)
    pdf.cell(30,15,'Tablice pixeli:')
    pdf.ln(10)
    pdf.x = 5
    img1 = cv2.imread(''.join([location, '\\fig1.png']))
    img2 = cv2.imread(''.join([location, '\\fig2.png']))
    figure = np.concatenate((img1, img2), axis=1)
    cv2.imwrite('out.png', figure)
    pdf.image('out.png', x= None, y = None, w=pdf.w/1.1,h=pdf.h/4.0)
    os.remove("out.png")
    pdf.output(x+'.pdf', 'F')
    
######################################### KOD
print('Analiza kolorów elementów stron internetowych')
while True:
    print('Czy chcesz podać adres strony?')
    x = input('(Tak/Nie)')
    if x=='Tak':
        print('Podaj adres strony:')
        y = input('http://')
        operations(y)
        break
    elif x=='Nie':
        print('Wczytywanie stron z pliku strony.txt.')
        with open('strony.txt') as f:
            content = f.readlines()
            content = [z.strip() for z in content] 
        for z in content:
            operations(z)
        break
    else:
        continue

