import cv2
import numpy as np
from mss import mss

#Change to your desired screen position/size
mon = {'top':355, 'left':673, 'width':574, 'height':400}
sct = mss()
isPlaying = False
isFirst = True

prevpolygons = []
while 1:
	
	img = np.array(sct.grab(mon))
	img = img[35:,:,:]
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray, (11,11), 0)
	thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)[1]
	_, contours, res = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	if(not isFirst):
		prevpolygons = np.copy(polygons)
	polygons = []
	i = 0
	for cnt in contours:
		perimeter = cv2.arcLength(cnt, True)
		polygons.append(cv2.approxPolyDP(cnt, 0.1*perimeter, True))
		if len(polygons[i]) == 3:
			cv2.drawContours(img, polygons, i, (255,0,255), 1)
		else:
			cv2.drawContours(img, polygons, i, (0,255,0), 3)	
		i = i + 1

		if(not isFirst and isPlaying):
			for polygon in polygons:
				# Get center of current polygon
				M = cv2.moments(polygon)
				cx = 0
				cy = 0
				cx2 = 0
				cy2 = 0
				if(M['m00'] != 0):
					cx = int(M['m10']/M['m00'])
					cy = int(M['m01']/M['m00'])
				minDist = float('inf')
				myPoly = []

				for prevpoly in prevpolygons:
					#find closest polygon
					M2 = cv2.moments(prevpoly)
					if(M2['m00'] != 0):
						cx2 = int(M2['m10']/M2['m00'])
						cy2 = int(M2['m01']/M2['m00'])
					dist = np.sqrt(np.power(cx2-cx,2)+np.power(cy2-cy,2))
					if(dist < minDist):
						minDist = dist
						myPoly = prevpoly

				if(len(myPoly) > 0):
					M2 = cv2.moments(myPoly)
					if(M2['m00'] != 0):
						cx2 = int(M2['m10']/M2['m00'])
						cy2 = int(M2['m01']/M2['m00'])

				xSpeed = cx - cx2
				ySpeed = cy - cy2
				cv2.line(img, (cx,cy),(cx2,cy2),(255,255,0),2)

		#Find the player
		if(isPlaying):
			closestAst = []
			minDistAst = 99999
			opposite = []
			minX = 0 
			minY = 0
			for polygon in polygons :
				#Center of polygon
				cx = 0
				cy = 0
				M = cv2.moments(polygon)
				if(M['m00'] != 0):
					cx = int(M['m10']/M['m00'])
					cy = int(M['m01']/M['m00'])
				#If it's a triangle not on the border, so it should be the player's ship
				if(len(polygon) == 3 and cy > 40 and cy < 320 and cx > 60 and cx < 504):
					#Find shortest line.
					dist = []
					p = polygon
					font = cv2.FONT_HERSHEY_COMPLEX_SMALL
					#Label points for debugging purposes
					#cv2.putText(img,'0',(p[0][0][0], p[0][0][1]), font, 1,(255,255,255),1,cv2.LINE_AA)
					#cv2.putText(img,'1',(p[1][0][0], p[1][0][1]), font, 1,(255,255,255),1,cv2.LINE_AA)
					#cv2.putText(img,'2',(p[2][0][0], p[2][0][1]), font, 1,(255,255,255),1,cv2.LINE_AA)
					dist.append(np.sqrt(np.power(p[1][0][0]-p[0][0][0],2)+np.power(p[1][0][1]-p[0][0][1],2)))
					dist.append(np.sqrt(np.power(p[2][0][0]-p[1][0][0],2)+np.power(p[2][0][1]-p[1][0][1],2)))
					dist.append(np.sqrt(np.power(p[0][0][0]-p[2][0][0],2)+np.power(p[0][0][1]-p[2][0][1],2)))
					minDist = 0 #The index of the min distance
					#Easiest way for only three points
					if(dist[1] < dist[minDist]):
						minDist = 1
					if(dist[2] < dist[minDist]):
						minDist = 2

					#Find center of line point
					center = (0,0)
					opposite = (0,0)
					if(minDist == 0):
						center = ((p[1][0][0]+p[0][0][0])/2, (p[1][0][1]+p[0][0][1])/2)
						opposite = p[2]
					elif(minDist==1):
						center = ((p[2][0][0]+p[1][0][0])/2, (p[2][0][1]+p[1][0][1])/2)
						opposite = p[0]
					else:
						center = ((p[2][0][0]+p[0][0][0])/2, (p[2][0][1]+p[0][0][1])/2)
						opposite = p[1]

					#Find line between shortest line center and centeroid.
					#Find direction and print a line.
					cv2.line(img,center,(opposite[0][0],opposite[0][1]),(0,255,255),1)

				#####################################
				if(len(opposite) != 0):
					#Now find closest asteroid to player#
					distAst = np.sqrt(np.power(opposite[0][0] - cx,2) + np.power(opposite[0][1] - cy,2))
					if(distAst < minDistAst) :
						minX = cx
						miny = cy
			#Display line from asteroid to player
			if(len(opposite) != 0):
				cv2.line(img, (minX, minY), (opposite[0][0],opposite[0][1]), (120, 255, 50),2)


	
	cv2.imshow('Screen', img)
	isFirst = False
	k = cv2.waitKey(30)
	if (k & 0xFF) == 27:
		break
	elif (k & 0xFF) == 126:
		isPlaying = True 

cv2.destroyAllWindows()
