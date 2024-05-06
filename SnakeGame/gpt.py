import math
import random
import cvzone
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8, maxHands=1)

class SnakeGameClass:
    def __init__(self, pathFood):
        self.points = []  # Snake points list
        self.lengths = []  # Distance between points
        self.currentLength = 0  # Snake length
        self.allowedLength = 200  # Maximum allowed length
        self.previousHead = 0, 0  # Previous head point

        self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)
        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = 0, 0
        self.randomFoodLocation()

        self.score = 0
        self.gameOver = False

    def randomFoodLocation(self):
        self.foodPoint = random.randint(100, 1000), random.randint(100, 600)

    def update(self, imgMain, currentHead):
        if self.gameOver:
            cvzone.putTextRect(imgMain, 'Game Over', [300, 400],
                               scale=7, thickness=5, offset=20)
            cvzone.putTextRect(imgMain, f'Puntuación:{self.score}', [300, 550],
                               scale=7, thickness=5, offset=20)
        else:
            px, py = self.previousHead
            cx, cy = currentHead

            self.points.append([cx, cy])
            distance = math.hypot(cx - px, cy - py)
            self.lengths.append(distance)
            self.currentLength += distance
            self.previousHead = cx, cy

            # Snake length reduction
            if self.currentLength > self.allowedLength:
                for i, lenght in enumerate(self.lengths):
                    self.currentLength -= lenght
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break

            # Did the snake eat the food?
            rx, ry = self.foodPoint
            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and \
                    ry - self.hFood // 2 < cy < ry + self.hFood // 2:
                self.randomFoodLocation()
                self.allowedLength += 100
                self.score += 1

            # Draw the snake
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:
                        # Drawing all lines
                        cv2.line(imgMain, self.points[i - 1], self.points[i], (0, 0, 255), 20)
                cv2.circle(imgMain, self.points[-1], 20, (200, 0, 200), cv2.FILLED)

            # Draw food
            rx, ry = self.foodPoint
            imgMain = cvzone.overlayPNG(imgMain, self.imgFood, (rx - self.wFood // 2, ry - self.hFood // 2))

            cvzone.putTextRect(imgMain, f'Puntos:{self.score}', [50, 80],
                               scale=7, thickness=5, offset=20)

            # Did the snake die?
            pts = np.array(self.points[:-10], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(imgMain, [pts], False, (0, 200, 0), 3)
            minDist = cv2.pointPolygonTest(pts, (cx, cy), True, )  # Pass all our points and the head

            if -1 <= minDist <= 1:
                self.gameOver = True
                self.points = []  # Snake points list
                self.lengths = []  # Distance between points
                self.currentLength = 0  # Snake length
                self.allowedLength = 200  # Maximum allowed length
                self.previousHead = 0, 0  # Previous head point
                self.randomFoodLocation()
                self.score = 0

        return imgMain


game = SnakeGameClass('C:\\Users\\imsmo\\PycharmProjects\\CVProjects\\res\\star.png')

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_copy = img.copy()  # Make a copy of the original image

    hands, _ = detector.findHands(img_copy, flipType=False)

    if hands:
        lmlist = hands[0]['lmList']
        pointIndex = lmlist[8][0:2]
        img = game.update(img_copy, pointIndex)

    cv2.imshow('Snake Game', img)

    key = cv2.waitKey(1)
    if key == ord('r'):
        game.gameOver = False

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
