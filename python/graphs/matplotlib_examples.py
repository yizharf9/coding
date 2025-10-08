import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d as plt_3d
from matplotlib.animation import PillowWriter

ax = plt.axes(projection="3d")

length = 10
density = 0.01*np.pi

# X=np.arange(-3*np.pi,3*np.pi,0.01)
X_rand=np.random.randint(-50,50,2*10**3)*0.05
Y_rand=np.random.randint(-50,50,2*10**3)*0.05
Z_rand=np.random.randint(-50,50,2*10**3)*0.05

# X=np.linspace(-2,2,100)
# Y=np.linspace(-2,2,100)
# Z=np.linspace(-2,2,100)

X=np.arange(-length,length,density)
Y=np.arange(-length,length,density)
Z=np.arange(-length,length,density)


Y=np.arange(-length,length,density)


def f(x,y) :
    return np.exp(-(x**2 +y**2))
def g(x,y) :
    return np.sin(x)*np.cos(y)
def h(x,y) :
    return np.sin((x**2+y**2))/((x**2+y**2+1e-10)**0.5)
def u(r,p) :
    return 3-r**2*np.cos(2*p)+2*r**4*np.cos(4*p)

F=f(X_rand,Y_rand)
G=g(X_rand,Y_rand)
H=h(X_rand,Y_rand)
U=u(X_rand,Y_rand)
# ax.scatter(X_rand,Y_rand,F,alpha=0.3)

_X,_Y = np.meshgrid(X,Y)
_Z = _X*_Y
_F = f(_X,_Y)
_G = g(_X,_Y)

# polar coordinates:
R = np.sqrt((_X**2+_Y**2) * (_X**2+_Y**2<=1)) 


Phi = np.arctan(_Y/_X)
_U = u(R,Phi)


ax.plot_surface(_X,_Y,_G,alpha=1,cmap="plasma")
# ax.plot_surface(_X,_Y,_H,alpha=1,cmap="plasma")
# plt.scatter(_X,_Y,_H,)
plt.show()




def psi(x,t):
    return np.sin(x-t)

x= np.linspace(0,10*np.pi,1000)

# fig,ax = plt.subplots(1,1,figsize=(8,4)) #design and measurements
# ln1 = plt.plot([],[])
# time_text = ax.text(0.65,0.95,'',fontsize=15,transform=ax.transAxes,)
    








