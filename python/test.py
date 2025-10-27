# # # import pandas as pd
# # import random 
# # import networkx as nx

# # N = 10
# # nodes = [((i)//N,(i+1)//N) for i in range(N)]

# # G = nx.Graph(nodes)

# # nx.draw(G)
# # nx.fl














# # class Node():
# #     def __init__(self,key,left = None,right = None,parent = None ):
# #         self.left = left
# #         self.right = right
# #         self.parent = parent
# #         self.key = key
# #     def is_leaf(self):
# #         return not self.has_left() and not self.has_right()
# #     def has_left(self):
# #         return self.left is not None
# #     def has_right(self):
# #         return self.right is not None
# #     def has_parent(self):
# #         return self.right is not None
# # class Tree():
# #     def __init__(self,root : Node ,nodes = [] ):
# #         self.root = root
# #         if len(nodes) != 0:
# #             for node in nodes:
# #                 self.insert(node)
    
# #     def insert(self,x : Node):
# #         self.rec_insert(x,self.root)
        
# #     def rec_insert(self,x : Node,y : Node):
# #         # if y.is_leaf() :
# #         if y.key <= x.key :
# #             if not y.has_right() :
# #                 y.right = x
# #                 x.parent = y
# #             else : 
# #                 self.rec_insert(x,y.right)
                    
# #         if y.key > x.key :
# #             if not y.has_left() :
# #                 y.left = x
# #                 x.parent = y
# #             else : 
# #                 self.rec_insert(x,y.left)
                    
        
# #     def tarversal(self,t):
# #         if t == "post":
# #             self.rec_postorder(self.root)
# #         if t == "in":
# #             self.rec_inorder(self.root)
# #         if t == "pre":
# #             self.rec_preorder(self.root)
        
# #     def rec_inorder(self,x : Node):
# #         if not x.has_right() and not x.has_left():
# #             print(x.key)
# #             return
# #         if x.has_left() : 
# #             self.rec_inorder(x.left) 
        
# #         print(x.key)
        
# #         if x.has_right() : 
# #             self.rec_inorder(x.right)
        
# #     def rec_postorder(self,x : Node):
# #         print(x.key)
# #         if not x.has_right() and not x.has_left():
# #             return
# #         if x.has_left() : 
# #             self.rec_inorder(x.left) 
# #         if x.has_right() : 
# #             self.rec_inorder(x.right)
            
# #     def rec_preorder(self,x : Node):
# #         if not x.has_right() and not x.has_left():
# #             return
# #         if x.has_left() : 
# #             print(x.key)
# #             self.rec_inorder(x.left) 
# #         else:
# #             print(x.key)
# #         if x.has_right() : 
# #             self.rec_inorder(x.right)


# # # a = Node(1)
# # # b = Node(2)
# # # c = Node(3)
# # # d = Node(0)
# # # e = Node(4)
# # # nodes = [b,c,d,e]
# # # N = 7
# # # nodes = [Node(i) for i in range(1,N+1)]
# # # root = nodes[N//2]
# # # nodes.pop(N//2)
# # # random.shuffle(nodes)
# # # print(f"root is {root.key}")
# # # for node in nodes :
# # #     print(node.key)
# # # print()

# # # T = Tree(root,nodes)
# # # # T.tarversal("in")
# # # # T.tarversal("post")
# # # T.tarversal("pre")
# # # print()
# # # print(nodes[3].parent.key)


# import sys
# import numpy as np
# import matplotlib.pyplot as plt
# from numpy.fft import fft2, ifft2, fftshift, ifftshift
# from math import pi, sqrt

# # הדפסה קצרה לבקרה שה-interpreter הנכון נטען
# print("PYTHON:", sys.executable)

# # ===================== פרמטרים ניתנים לשינוי =====================

# # גיאומטריה
# ELEV_DEG   = 60.0        # elevation (מעלות)
# H_SAT_M    = 200e3       # גובה לווין [m]
# H_TURB_TOP = 30e3        # טווח גבהים עם טורבולנציה [m]

# # אופטיקה
# LAM        = 1550e-9     # אורך גל [m]

# # פרופיל HV5/7 (יבשתי) + von-Kármán
# HV57_A     = 1.7e-14     # ground term [m^(-2/3)]
# HV57_V     = 21.0        # RMS wind [m/s]
# L0         = 100.0       # outer scale [m]
# l0         = 0.002       # inner scale [m]

# # phase screens
# NUM_SCREENS  = 24
# REALIZATIONS = 6         # מס' מימושים להממוצע

# # רשת חישוב
# N  = 256                 # grid size (N×N)
# DX = 0.10                # מרווח דגימה במישור המקור [m] (חלון ≈ N*DX)

# # סריקות לאיור A1/A2
# DT_VALUES    = np.array([0.08, 0.12, 0.16, 0.20, 0.30, 0.40])                # קוטר משדר [m]
# DR_VALUES    = np.array([0.08, 0.12, 0.16, 0.20, 0.30, 0.40, 0.60, 0.80])    # קוטר מקלט [m]
# DT_BASELINE  = 0.20
# DR_BASELINE  = 0.20

# # שמות קבצים
# FIG_A1 = "A1_ps_calibrated.png"
# FIG_A2 = "A2_ps_calibrated.png"

# # ===================== נגזרות וחישוב מקדים =====================

# k = 2.0 * pi / LAM
# L_TOTAL = H_SAT_M / np.sin(np.deg2rad(ELEV_DEG))
# L_TURB  = H_TURB_TOP / np.sin(np.deg2rad(ELEV_DEG))
# L_VAC   = max(L_TOTAL - L_TURB, 0.0)

# k0 = 1.0 / L0
# km = 5.92 / l0

# x  = (np.arange(-N//2, N//2)) * DX
# X, Y = np.meshgrid(x, x)

# fx = fftshift(np.fft.fftfreq(N, d=DX))
# FX, FY = np.meshgrid(fx, fx)
# FSQ    = FX**2 + FY**2

# KX = 2*np.pi*FX
# KY = 2*np.pi*FY
# K2 = KX**2 + KY**2

# # ===================== פונקציות מודל =====================

# def Cn2_HV57(h: np.ndarray) -> np.ndarray:
#     """HV5/7 land profile: Cn^2(h) עם h במטרים."""
#     return (0.00594*(HV57_V/27.0)**2*(1e-5*h)**10*np.exp(-h/1000.0)
#             + 2.7e-16*np.exp(-h/1500.0)
#             + HV57_A*np.exp(-h/100.0))

# def asm_transfer(dz: float) -> np.ndarray:
#     """Angular Spectrum (paraxial) transfer function."""
#     return np.exp(1j*k*dz) * np.exp(-1j*np.pi*LAM*dz*FSQ)

# def propagate(U: np.ndarray, dz: float) -> np.ndarray:
#     """תעבורת גל באמצעות ASM."""
#     return ifft2( fft2(U) * ifftshift(asm_transfer(dz)) )

# def launch_field(D_T: float) -> np.ndarray:
#     """שיגור Gaussian: w0 = D_T/2 (רדיוס 1/e^2)."""
#     w0 = D_T/2.0
#     return np.exp(-(X**2 + Y**2)/w0**2)

# def phase_screen_vk_calibrated(dz: float, Cn2_val: float, rng: np.random.Generator) -> np.ndarray:
#     """
#     מסך פאזה von-Kármán לשכבה dz עם Cn^2 נתון.
#     מכויל כך ש-Var[phi] יתאים לאינטגרל התאורטי של Φ_φ.
#     """
#     Phi_n  = 0.033 * Cn2_val * (K2 + k0**2)**(-11/6.0) * np.exp(-K2/(km**2))
#     Phi_ph = 2*np.pi * (k**2) * dz * Phi_n

#     dfx = float(fx[1] - fx[0])
#     dfy = dfx
#     var_theory = np.sum(Phi_ph) * (dfx*dfy)

#     W    = (rng.normal(size=(N,N)) + 1j*rng.normal(size=(N,N))) / sqrt(2.0)
#     Fphi = W * np.sqrt(Phi_ph) * (dfx*dfy)**0.5
#     phi_raw = np.real(ifft2(ifftshift(Fphi))) * (N*DX)**2

#     var_emp = np.var(phi_raw)
#     scale   = 1.0 if (var_emp <= 0.0 or var_theory <= 0.0) else np.sqrt(var_theory/var_emp)
#     return np.exp(1j * (phi_raw * scale))

# def encircled_energy(I: np.ndarray, a_R: float) -> float:
#     """יחס אנרגיה בתוך פתח עגול ברדיוס a_R."""
#     R = np.sqrt(X**2 + Y**2)
#     return float((I * (R <= a_R)).sum() / I.sum())

# def eta_propagate(D_T: float, D_R: float, use_turb: bool,
#                   Cn2_layers: np.ndarray, dz_s: float,
#                   realizations: int = REALIZATIONS, seed0: int = 1234) -> float:

a = np.array([])