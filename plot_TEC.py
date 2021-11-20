from matplotlib.pyplot import *
import mpld3
import numpy as np
import datetime
from astropy import modeling

#Plotting routine for the generated TEC dataset..

d               =       datetime.datetime.today() - datetime.timedelta(days=1)
TEC_file        =       'TEC_NOV03_2021_v1.txt'#'TEC_DATA/TEC_REC_date_25_9'#'TEC_TECONLY_date'+str(d.day)+'_'+str(d.month)+'_'+str(d.year)
TEC             =       np.loadtxt(TEC_file)#/10**16
time            =       (TEC[:,0]/(3600.0*24))
x               =       TEC[:,0][np.where(TEC[:,11]>50)]
y               =       TEC[:,2][np.where(TEC[:,11]>50)]
data            =       np.array([x/(3600.0*24), y/10**16])
fitter          =       modeling.fitting.LevMarLSQFitter()
model           =       modeling.models.Gaussian1D()
fitted_model    =       fitter(model, x/(3600.0*24), y/10**16)

fig             =       figure(figsize=(12, 7))
subplot(2, 1, 1)
color           =       'tab:green'
color1          =       'tab:red'
xlabel('Time of the week / Fractional Day', fontsize=16)
ylabel('TECU / 10**16 el/m^2', color=color, fontsize=16)
plot(x/(3599.0*24), y/10**16 , color=color, label='Data')
plot(x/(3600.0*24), fitted_model(x/(3600.0*24)), label='Curve fit', color=color1)
tick_params(axis='y', labelcolor=color)
grid()
legend()


subplot(2, 1, 2)
color = 'tab:blue'
ylabel('Ionospheric Time delay / mu sec', color=color, fontsize=16)  # we already handled the x-label with ax1
plot(x/(3600.0*24),  TEC[:,1][np.where(TEC[:,11]>50)]/10**-6 , color=color, label='Ionospheric time delay')
tick_params(axis='y', labelcolor=color)
grid()
legend()


#fig            =       figure();plot(time, TEC[:,1], 'x');grid();xlabel('Time of the week / sec');ylabel('TECU / 10**16 el/m^2');title(str(d.day)+'-'+str(d.month)+'-'+str(d.year));
savefig(str(d.day)+'-'+str(d.month)+'-'+str(d.year)+'.png')
html_str = mpld3.fig_to_html(fig)
Html_file= open("index.html","w+")
Html_file.write('<body style="background-color:powderblue;">\n<h1>Single Frequency GPS based TEC Measurment</h1>\n<h2>Daily TEC plot</h2>')
Html_file.write(html_str)
Html_file.write('<h2>References</h2>')
Html_file.write('<h3>[1] J. A. Klobuchar, "Ionospheric Time-Delay Algorithm for Single-Frequency GPS Users," in IEEE Transactions on Aerospace and Electronic Systems, vol. AES-23, no. 3, pp. 325-331, May 1987, doi: 10.1109/TAES.1987.310829 </h3>')
Html_file.write('<h3>[2] <a href=" https://gssc.esa.int/navipedia/index.php/Klobuchar_Ionospheric_Model"> https://gssc.esa.int/navipedia/index.php/Klobuchar_Ionospheric_Model</a></h3>')
Html_file.write('<style>\n.bottom-three {\nmargin-bottom: 3cm;\n}\n</style>\n')
Html_file.write('<h4>If you find any issues with the dataset please contact: </h4>')

Html_file.close()

