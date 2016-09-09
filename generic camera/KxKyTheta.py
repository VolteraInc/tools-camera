from math import cos,sin, asin, sqrt, degrees, tan
import numpy as np
from shapely.geometry import Polygon


# Global parameters
Cx = 100.0;
Cy = 100.0;

	# p2     d2_2     p3

	# d1_1   d3_1     d1_2

	# p1     d2_1     p4

class point():
	def __init__(self, x, y):
		self.x = x
		self.y = y

class truePCB():

	def __init__(self):
		self.x1 = (141.03)
		self.y1 = (110.86)

		self.x2 = (141.06)
		self.y2 = (11.05)

		self.x3 = (19.52)
		self.y3 = (11.05)

		self.x4 = (19.49)
		self.y4 = (110.86)

		self.d1_1 = sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)
		self.d1_2 = sqrt((self.x4 - self.x3)**2 + (self.y4 - self.y3)**2)
		self.d2_1 = sqrt((self.x4 -self.x1)**2 + (self.y4 - self.y1)**2)
		self.d2_2 = sqrt((self.x2 -self.x3)**2 + (self.y2 - self.y3)**2)
		self.d3_1 = sqrt((self.x3 -self.x1)**2 + (self.y3 - self.y1)**2)
		self.d3_2 = sqrt((self.x4 - self.x2)**2 + (self.y4 - self.y2)**2)

		self.area = Polygon([(self.x1, self.y1), (self.x2, self.y2), (self.x3, self.y3), (self.x4, self.y4)]).area

def calculateParameters(vA, vB, vC, dA, dB, dC):

	''' Our equation is of the form:

	aG + bH + 2abI = c
	dG + eH + 2deI = f
	gG + hH + 2ghI = j
	'''

	a = vA.x
	b = vA.y
	c = dA**2

	d = vB.x
	e = vB.y
	f = dB**2

	g = vC.x
	h = vC.y
	j = dC**2

	coeffs = np.array([[a**2, b**2, 2*a*b], [d**2 ,e**2 ,2*d*e], [g**2, h**2, 2*g*h]])
	equals = np.array([c, f ,j])

	G, H, I = np.linalg.solve(coeffs,equals)

	Kx = sqrt(G*Cx**2)
	Ky = sqrt(H*Cy**2)
	theta_rads = asin(I*Cx*Cy/(Kx * Ky))

	return Kx, Ky, theta_rads

def calcStepsFromCoords(X, Y):
	''' Calculates Absolute steps from coordinates given our calculated Kx, Ky, theta_rads '''
	xs = int(X * Cx / (Kx*cos(theta_rads)));
	ys = int((Y - X*tan(theta_rads))*Cy/Ky)
	return xs, ys

def calcCoordsFromSteps(steps_x, steps_y, Kx, Ky, theta_rads):
	''' Calculates coordinates from absolute steps given our calculated Kx, Ky, theta_rads '''
	X = Kx*steps_x*cos(theta_rads)/Cx
	Y = Kx*steps_x*sin(theta_rads)/Cx + Ky*steps_y/Cy
	return X, Y

def calcRelativeToFirstPoint(p1, p2, p3, p4, flip=False):
	''' Naming convention follows distances'''
	v1 = point(p2.x - p1.x, p2.y - p1.y)
	v2 = point(p4.x - p1.x, p4.y - p1.y)
	v3 = point(p3.x - p1.x, p3.y - p1.y)

	if flip:
		v1 = point(-v1.x, -v1.y)
		v2 = point(-v2.x, -v2.y)
		v3 = point(-v3.x, -v3.y)
	return v1, v2, v3

def calculateKxKyTheta(x1, y1, x2, y2, x3, y3, x4, y4):
	#These are steps coordinates for eyeballed measured values.
	# p1 = point(330, 5650)
	# p2 = point(330, 15650)
	# p3 = point(10008, 15650)
	# p4 = point(10000, 5650)

	# Values after the X axis rail was adjusted.
	p1 = point(x1, y1)
	p2 = point(x2, y2)
	p3 = point(x3, y3)
	p4 = point(x4, y4)

	# Calculate our true distances given the PCB gerber
	t = truePCB()


	# Calculate our relative vectors
	v1, v2, v3 = calcRelativeToFirstPoint(p1, p2, p3, p4)

	#Calculate given the vectors.
	Kx_1, Ky_1, theta_rads_1 = calculateParameters(v1, v2, v3, t.d1_1, t.d2_1, t.d3_1)
	print("First set: ", Kx_1, Ky_1, theta_rads_1)

	# Calculate our relative vectors to p3 now. Other points are in clockwise order
	v1, v2, v3 = calcRelativeToFirstPoint(p3, p4, p1, p2, flip=True)

	#Calculate given the vectors
	Kx_2, Ky_2, theta_rads_2 = calculateParameters(v1, v2, v3, t.d1_2, t.d2_2, t.d3_1)
	print("Second set: ", Kx_2, Ky_2, theta_rads_2)


	# Average the results
	Kx = (Kx_1 + Kx_2) / 2.0
	Ky = (Ky_1 + Ky_2) / 2.0
	theta_rads = (theta_rads_1 + theta_rads_2)/ 2.0
	print("Averaged: ", Kx, Ky, theta_rads)


	# Convert our absolute measured steps into coords.
	x1, y1 = calcCoordsFromSteps(p1.x, p1.y, Kx, Ky, theta_rads)
	x2, y2 = calcCoordsFromSteps(p2.x, p2.y, Kx, Ky, theta_rads)
	x3, y3 = calcCoordsFromSteps(p3.x, p3.y, Kx, Ky, theta_rads)
	x4, y4 = calcCoordsFromSteps(p4.x, p4.y, Kx, Ky, theta_rads)

	# Compute our distances given our calculated coordinates
	d1_1 = sqrt((x2- x1)**2 + (y2 - y1)**2)
	d1_2 = sqrt((x4- x3)**2 + (y4 - y3)**2)
	d2_1 = sqrt((x4 -x1)**2 + (y4 - y1)**2)
	d2_2 = sqrt((x2 -x3)**2 + (y2 - y3)**2)
	d3_1 = sqrt((x3 -x1)**2 + (y3 - y1)**2)
	d3_2 = sqrt((x4- x2)**2 + (y4 - y2)**2)

	# Print our delta's.
	print("Error in calculated and true distances:")
	print(round(d1_1 - t.d1_1,4))
	print(round(d1_2 - t.d1_2,4))
	print(round(d2_1 - t.d2_1,4))
	print(round(d2_2 - t.d2_2,4))
	print(round(d3_1 - t.d3_1,4))
	print(round(d3_2 - t.d3_2,4))
	
	return Kx, Ky, theta_rads

